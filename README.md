# Easy AI

This repository contains tools for interacting with Tally and a small backend service for managing voucher upload tasks.

## Backend Service

The `backend` package exposes a FastAPI application with a few routes used by the agent:

- `POST /upload_voucher` – upload voucher data (JSON or XML).
- `GET /tasks` – retrieve pending voucher tasks for insertion.
- `POST /sync_status` – update the last sync time and Tally access status.
- `GET /dashboard` – simple HTML dashboard showing client information.

All API requests must include a `Bearer` token in the `Authorization` header. A
unique token is generated for every client and stored in the `clients` table.

To run the server:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The application stores its data in `backend/backend.db` (SQLite).

## Agent Configuration

The agent reads its backend credentials from environment variables:

```
BACKEND_URL=https://example.com
CLIENT_ID=<your_client_id>
CLIENT_TOKEN=<generated_token>
```

When the agent makes a request to the backend it automatically includes
`CLIENT_TOKEN` in the `Authorization` header.
