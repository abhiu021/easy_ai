from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime
from pathlib import Path
import json
import os
import pdfkit
import requests
from twilio.rest import Client as TwilioClient
from .agent_helper import process_text

from .database import (
    init_db,
    upsert_client,
    add_task,
    add_voucher,
    update_sync,
    get_clients,
    get_pending_tasks,
    get_rejected_tasks,
    get_client_by_token,
    get_voucher,
)

app = FastAPI()

templates = Jinja2Templates(directory=str((__file__).rsplit('/',1)[0]+"/templates"))
conn = init_db()

# Directory for storing generated invoices
INVOICE_DIR = Path(__file__).parent / "invoices"
INVOICE_DIR.mkdir(exist_ok=True)

# Twilio configuration from environment variables
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Gupshup configuration
GUPSHUP_API_BASE = os.getenv("GUPSHUP_API_BASE", "https://api.gupshup.io")
GUPSHUP_API_KEY = os.getenv("GUPSHUP_API_KEY")
GUPSHUP_SOURCE = os.getenv("GUPSHUP_SOURCE")
GUPSHUP_SRC_NAME = os.getenv("GUPSHUP_SRC_NAME")

REQUIRED_FIELDS = {"vchtype", "date", "party", "amount"}


def authenticate(request: Request) -> str:
    """Validate the Authorization header and return the client_id."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ", 1)[1]
    client = get_client_by_token(conn, token)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid token")
    return client["client_id"]

@app.post("/upload_voucher")
async def upload_voucher(
    request: Request,
    client_id: str = Form(...),
    data_type: str = Form("json"),
    company_name: Optional[str] = Form(None),
    payload: str = Form(...),
):
    """Receive voucher data and store as a task."""
    auth_client = authenticate(request)
    if auth_client != client_id:
        raise HTTPException(status_code=403, detail="Token does not match client")
    upsert_client(conn, client_id, company_name)
    status = "pending"
    missing_fields = None

    if data_type == "json":
        try:
            import json
            data = json.loads(payload)
            missing = [f for f in REQUIRED_FIELDS if f not in data]
            if missing:
                status = "rejected"
                missing_fields = ",".join(missing)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
    task_id = add_task(conn, client_id, payload, data_type, status=status, missing_fields=missing_fields)
    voucher_id = add_voucher(conn, client_id, payload)
    return {"task_id": task_id, "voucher_id": voucher_id, "status": status}


@app.get("/tasks")
async def get_tasks(request: Request):
    client_id = authenticate(request)
    tasks = get_pending_tasks(conn, client_id)
    return [dict(t) for t in tasks]


@app.post("/sync_status")
async def sync_status(request: Request, data: dict):
    auth_client = authenticate(request)
    client_id = data.get("client_id") or auth_client
    if client_id != auth_client:
        raise HTTPException(status_code=403, detail="Token does not match client")
    last_sync = data.get("last_sync") or datetime.utcnow().isoformat()
    tally_ok = bool(data.get("tally_access_ok"))
    upsert_client(conn, client_id)
    update_sync(conn, client_id, last_sync, tally_ok)
    return {"status": "ok"}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    clients = get_clients(conn)
    rejected = get_rejected_tasks(conn)
    reject_map = {}
    for r in rejected:
        cid = r["client_id"]
        reject_map.setdefault(cid, []).append(r["missing_fields"])
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "clients": clients,
            "rejected": reject_map,
        },
    )


def generate_invoice(voucher_row) -> Path:
    """Render invoice HTML and convert to PDF."""
    pdf_path = INVOICE_DIR / f"{voucher_row['id']}.pdf"
    if pdf_path.exists():
        return pdf_path
    html_content = templates.get_template("invoice.html").render(
        voucher=dict(voucher_row)
    )
    pdfkit.from_string(html_content, str(pdf_path))
    return pdf_path


@app.get("/invoice/{voucher_id}")
async def get_invoice(voucher_id: int):
    voucher = get_voucher(conn, voucher_id)
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    pdf_path = generate_invoice(voucher)
    return FileResponse(path=pdf_path, filename=f"invoice_{voucher_id}.pdf", media_type="application/pdf")


@app.post("/send_invoice/{voucher_id}")
async def send_invoice(voucher_id: int, phone: str = Form(...)):
    """Send the invoice PDF to the provided WhatsApp number via Twilio."""
    voucher = get_voucher(conn, voucher_id)
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    pdf_path = generate_invoice(voucher)
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_WHATSAPP_NUMBER):
        raise HTTPException(status_code=500, detail="Twilio not configured")
    client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{phone}",
        body="Here is your invoice",
        media_url=[f"file://{pdf_path}"]
    )
    return {"sid": message.sid}


@app.post("/gupshup")
async def gupshup_webhook(request: Request):
    """Receive Gupshup webhook and respond using the agent."""
    data = await request.json()
    # Extract message text and sender number
    message = (
        data.get("payload", {})
        .get("payload", {})
        .get("text")
        or data.get("text")
    )
    sender = data.get("payload", {}).get("source")
    if not message or not sender:
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Process the incoming text with the agent
    reply = await process_text(message)

    if not (GUPSHUP_API_KEY and GUPSHUP_SOURCE):
        raise HTTPException(status_code=500, detail="Gupshup not configured")

    url = f"{GUPSHUP_API_BASE}/api/v1/msg"
    headers = {"apikey": GUPSHUP_API_KEY}
    payload = {
        "channel": "whatsapp",
        "source": GUPSHUP_SOURCE,
        "destination": sender,
        "message": reply,
    }
    if GUPSHUP_SRC_NAME:
        payload["src.name"] = GUPSHUP_SRC_NAME
    resp = requests.post(url, data=payload, headers=headers)
    resp.raise_for_status()
    return {"status": "ok"}


