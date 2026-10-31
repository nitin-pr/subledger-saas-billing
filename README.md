# SubLedger — SaaS Subscription & Billing System

A simplified SaaS billing backend: plans, customers, subscriptions,
invoices, payment attempts, and an append-only ledger. FastAPI + SQLAlchemy,
built LLD-first — see [DESIGN.md](DESIGN.md) for the ERD, service/repository
responsibility tables, business-rule ownership, and the invoice/payment
flows.

This project is fully independent of any other project in this repo — its
own virtualenv, its own database, its own git history.

## Stack

- FastAPI + Pydantic v2 (request/response validation, auto Swagger docs)
- SQLAlchemy 2.x (Repository pattern over the ORM)
- PostgreSQL 16 (via Docker)
- pytest + httpx (API-level tests against an in-memory SQLite DB — no
  Docker needed to run the test suite)
- python-dotenv / pydantic-settings for config

## Project layout

```
SubLedger/
├── app/
│   ├── main.py              # FastAPI app, routers, domain-error -> HTTP mapping
│   ├── config.py             # pydantic-settings, reads .env
│   ├── db.py                  # engine, SessionLocal, Base, get_db (commits/rolls back per request)
│   ├── models.py               # Plan, Customer, Subscription, Invoice, PaymentAttempt, LedgerEntry
│   ├── schemas.py               # Pydantic request/response models + field validators
│   ├── exceptions.py             # SubLedgerError subclasses -> HTTP status codes
│   ├── utils.py                   # billing-cycle period math
│   ├── dependencies.py             # DI wiring: repo -> service, via FastAPI Depends()
│   ├── repositories/                # one file per entity, extends BaseRepository
│   ├── services/                     # one file per entity, owns all business rules
│   └── routes/                        # thin: parse request -> call one service method -> return
├── tests/                   # 34 pytest tests (API-level, in-memory SQLite)
├── docker-compose.yml      # Postgres + pgAdmin + the API itself
├── Dockerfile
├── DESIGN.md               # LLD: ERD, responsibility tables, flows, class diagram
└── .env.example
```

## 1. Setup

### Prerequisites
- Python 3.11+ (tested on 3.14)
- Docker Desktop

### Local (non-Docker) run

```bash
cd SubLedger

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env
```

`.env` holds every DB/pgAdmin credential — nothing is hardcoded in
`app/config.py`.

Start Postgres (and pgAdmin) via Docker, then run the API locally against
it:

```bash
docker compose up -d db pgadmin
uvicorn app.main:app --reload
```

The app creates its tables automatically on startup (`Base.metadata.create_all`
in `app/main.py`'s lifespan handler) — no separate migration step needed for
this project's scope.

### Fully containerized run

```bash
docker compose up -d --build
```

This builds and starts three containers: `subledger_postgres`,
`subledger_pgadmin` (web UI at **http://localhost:5050** — log in with
`PGADMIN_EMAIL`/`PGADMIN_PASSWORD` from `.env`, then register a server with
host `db`, port `5432`, and the `DB_*` credentials), and `subledger_api`
(the FastAPI app itself, on port 8000).

## 2. API docs

FastAPI auto-generates interactive Swagger docs — once the server is
running:

- **http://localhost:8000/docs** (Swagger UI)
- **http://localhost:8000/openapi.json** (raw OpenAPI schema)

## 3. Required APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/plans` | Create a subscription plan |
| GET | `/plans` | List plans |
| PATCH | `/plans/{plan_id}` | Update/deactivate a plan |
| POST | `/customers` | Create a customer |
| GET | `/customers` | List customers |
| GET | `/customers/{customer_id}` | Fetch customer details |
| POST | `/subscriptions` | Create a subscription |
| GET | `/subscriptions` | List subscriptions |
| PATCH | `/subscriptions/{subscription_id}/cancel` | Cancel a subscription |
| POST | `/invoices/generate` | Generate an invoice for a subscription |
| GET | `/invoices/{invoice_id}` | Fetch invoice details |
| POST | `/payments/record` | Record a payment attempt |
| GET | `/customers/{customer_id}/ledger` | Fetch a customer's ledger history |

## 4. Business rules enforced

- Plan price must be greater than 0 (Pydantic validator, 422 if violated).
- Customer email must be unique (400 on duplicate).
- A subscription cannot be created for an inactive plan (400).
- A customer cannot have two active subscriptions to the same plan (400).
- An invoice's `amount_due` is a snapshot of the plan's price *at the
  moment the invoice is generated* — already-created invoices are never
  retroactively changed by a later plan price update.
- A successful payment cannot exceed an invoice's remaining unpaid amount
  (400).
- Full payment → invoice `status=paid`; partial payment →
  `status=partially_paid`.
- A failed payment never increases `amount_paid` or changes invoice status.
- Ledger entries are append-only and traceable via `reference_id`
  (`invoice:{id}` / `payment:{id}`) — no route or repository method in the
  app ever updates or deletes a `LedgerEntry`.

## 5. Automated tests

34 tests across 5 files, covering every business rule above plus 404/422
edge cases and the invoice/ledger traceability flows.

```bash
python -m pytest -v
```

Tests run against an in-memory SQLite database (overriding the `get_db`
dependency in `tests/conftest.py`) — no Docker or Postgres required to run
them.

## Assumptions and limitations

- No authentication/RBAC — out of scope per the brief (bonus-only).
- No real payment gateway integration — `PaymentService.record_payment`
  takes a `status` directly in the request, simulating what a gateway
  webhook would report.
- No proration on plan changes or mid-cycle cancellation — out of scope.
- `BillingCycle.CUSTOM` defaults the generated period to 30 days; there's
  no separate "custom interval" field since the brief doesn't specify one.
- Table creation uses `Base.metadata.create_all()` at startup rather than
  Alembic migrations — appropriate for this project's scope; a production
  version would add Alembic.
