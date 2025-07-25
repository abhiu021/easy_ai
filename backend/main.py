from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime

from .database import init_db, upsert_client, add_task, update_sync, get_clients, get_pending_tasks, get_rejected_tasks

app = FastAPI()

templates = Jinja2Templates(directory=str((__file__).rsplit('/',1)[0]+"/templates"))
conn = init_db()

REQUIRED_FIELDS = {"vchtype", "date", "party", "amount"}

@app.post("/upload_voucher")
async def upload_voucher(
    client_id: str = Form(...),
    data_type: str = Form("json"),
    company_name: Optional[str] = Form(None),
    payload: str = Form(...),
):
    """Receive voucher data and store as a task."""
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
async def get_tasks():
    tasks = get_pending_tasks(conn)
    return [dict(t) for t in tasks]


@app.post("/sync_status")
async def sync_status(data: dict):
    client_id = data.get("client_id")
    last_sync = data.get("last_sync") or datetime.utcnow().isoformat()
    tally_ok = bool(data.get("tally_access_ok"))
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id required")
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

