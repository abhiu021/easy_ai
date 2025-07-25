from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime

from .database import (
    init_db,
    upsert_client,
    add_task,
    update_sync,
    get_clients,
    get_pending_tasks,
    get_rejected_tasks,
    get_client_by_token,
)

app = FastAPI()

templates = Jinja2Templates(directory=str((__file__).rsplit('/',1)[0]+"/templates"))
conn = init_db()

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
    return {"task_id": task_id, "status": status}


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

