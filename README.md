# Easy AI

This repository contains tools for interacting with Tally and a small backend service for managing voucher upload tasks.

## Backend Service

The `backend` package exposes a FastAPI application with a few routes used by the agent:

- `POST /upload_voucher` – upload voucher data (JSON or XML).
- `GET /tasks` – retrieve pending voucher tasks for insertion.
- `POST /sync_status` – update the last sync time and Tally access status.
- `GET /dashboard` – simple HTML dashboard showing client information.

To run the server:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The application stores its data in `backend/backend.db` (SQLite).
