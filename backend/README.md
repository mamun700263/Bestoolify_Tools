# Tavdev Monitor — Backend

The backend service powering **Tavdev Monitor**, a lightweight uptime and API monitoring platform built for developers.

Live application: https://monitor.tavdev.com

The backend provides APIs for:

* Creating and managing monitoring targets
* Instantly checking the health of any URL
* Tracking response time and HTTP health
* Scheduling recurring checks
* Maintaining the last 24 hours of monitoring data
* Recording incidents and failed responses
* Exporting monitoring data
* User authentication and monitor limits

---

## Tech Stack

* **Python**
* **FastAPI**
* **PostgreSQL**
* **Redis**
* **SQLAlchemy**
* **Alembic**
* **JWT Authentication**
* **Google OAuth**
* **Docker**
* **Pytest**

---

## Architecture

Tavdev Monitor uses PostgreSQL as its persistent data store and Redis as a fast monitoring/scheduling layer.

```text
                    ┌─────────────────┐
                    │     Frontend    │
                    │    Next.js      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     FastAPI     │
                    │      API        │
                    └───────┬─────────┘
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
       ┌─────────────────┐      ┌─────────────────┐
       │   PostgreSQL    │      │      Redis      │
       │                 │      │                 │
       │ Users           │      │ Active monitors │
       │ Monitors        │      │ Ping history    │
       │ Persistent data │      │ Fast access     │
       └─────────────────┘      └────────┬────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │    Scheduler    │
                                │                 │
                                │ 1 / 2 / 5 / 10m │
                                └────────┬────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │ Monitored URLs  │
                                └─────────────────┘
```

### Why Redis?

The initial implementation repeatedly queried PostgreSQL for monitoring targets.

Instead of repeatedly loading monitor configuration from the database, active monitoring information is cached in Redis.

This allows the scheduler to access monitoring targets without continuously querying PostgreSQL.

PostgreSQL remains the persistent source of truth, while Redis provides the fast-access layer required by the monitoring process.

---

## Core Features

### Instant URL Health Check

The backend provides an unauthenticated endpoint for developers who simply want to check a URL.

It can be used similarly to a lightweight `curl` or Postman request.

```text
GET /test-ping?url=https://example.com
```

The response includes health information such as:

* Reachability
* Response time
* HTTP response information
* Check timestamp
* Error information when applicable

Authentication is **not required** for instant checks.

---

### Continuous Monitoring

Authenticated users can create persistent monitors.

A monitor contains information such as:

```text
URL
Monitoring interval
Account
Monitor status
```

Supported monitoring intervals currently include:

* 1 minute
* 2 minutes
* 5 minutes
* 10 minutes

The scheduler periodically checks active monitors and records their results.

---

## Monitoring History

Tavdev Monitor keeps monitoring information for the previous **24 hours**.

The system focuses particularly on unhealthy responses and incidents rather than treating every successful health check as equally valuable.

Users can inspect:

* Recent ping history
* Response information
* Failed checks
* Incidents
* Monitoring status

---

## Monitor Limits

Continuous monitoring requires authentication.

Each account currently receives a maximum of:

**10 monitors**

The limit exists both as a product constraint and as a resource-protection mechanism, preventing unrestricted users from creating large numbers of monitoring jobs and unnecessarily consuming database and monitoring resources.

Instant URL testing does not require an account.

---

## Authentication

The backend supports authenticated user accounts.

Authentication infrastructure includes:

* Email/password authentication
* Password hashing
* JWT-based authentication
* Access/refresh token flow
* Google OAuth

Authenticated endpoints use the current account dependency to verify ownership of monitors and protect account-specific resources.

Monitor resources are scoped to their owning account.

---

## API

The main monitoring API currently provides endpoints for:

| Method   | Endpoint                           | Purpose                       |
| -------- | ---------------------------------- | ----------------------------- |
| `GET`    | `/test-ping`                       | Instantly check a URL         |
| `POST`   | `/monitors`                        | Create a monitor              |
| `GET`    | `/monitors/{monitor_id}`           | Retrieve a monitor            |
| `PATCH`  | `/monitors/{monitor_id}`           | Update a monitor              |
| `DELETE` | `/monitors/{monitor_id}`           | Delete a monitor              |
| `GET`    | `/accounts/{account_id}/monitors`  | List account monitors         |
| `GET`    | `/monitors/{monitor_id}/pings`     | Retrieve 24-hour ping history |
| `GET`    | `/monitors/{monitor_id}/incidents` | Retrieve monitor incidents    |
| `GET`    | `/pings/download/{monitor_id}`     | Export ping data              |

The complete API specification is available through FastAPI's generated OpenAPI documentation when the backend is running.

---

## Data Export

Monitoring data can currently be exported as:

* JSON
* CSV
* Excel

The backend also contains infrastructure for additional integrations including:

* Google Sheets
* Database push
* API push

These integrations are kept separate from the core monitoring flow so that exporting monitoring data does not become a requirement for the monitoring system itself.

---

## Project Structure

```text
backend/
│
├── app/
│   ├── accounts/
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │   ├── jwt/
│   │   ├── oauth/
│   │   ├── models/
│   │   └── schemas/
│   │
│   ├── core/
│   │   ├── celery.py
│   │   ├── email/
│   │   ├── logger.py
│   │   └── redis.py
│   │
│   ├── db/
│   │   ├── engine.py
│   │   ├── base.py
│   │   └── registry.py
│   │
│   ├── uptime_keeper/
│   │   ├── caching/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── crud.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── scheduler.py
│   │   └── ping.py
│   │
│   ├── main.py
│   └── task_manager.py
│
├── alembic/
├── tests/
├── Dockerfile
├── Dockerfile-celery
├── docker-compose.yml
├── nginx/
├── pyproject.toml
├── requirements.txt
└── pytest.ini
```

The `uptime_keeper` package contains the core monitoring domain.

The `accounts` package handles authentication and account management.

The `core` package contains shared infrastructure such as logging, Redis, email, and background-task infrastructure.

---

## Local Development

### Requirements

You will need:

* Python
* PostgreSQL
* Redis
* Docker

The backend can be run using Docker for local development.

```bash
docker compose up
```

Environment-specific configuration should be supplied through environment variables.

**Never commit credentials, API keys, OAuth secrets, or database passwords to the repository.**

---

## Database

PostgreSQL stores persistent application data including:

* Account information
* Hashed passwords
* Monitor configurations
* Monitoring-related persistent records

Database schema changes are managed using **Alembic**.

```text
alembic/
└── versions/
```

---

## Redis

Redis is used as the high-speed monitoring layer.

The system synchronizes monitor configuration into Redis so the scheduler can access active monitoring targets without repeatedly querying PostgreSQL.

Redis is also used for monitoring-related cached/history data.

This architecture reduces unnecessary database reads and keeps the recurring monitoring workload lightweight.

---

## Scheduling

The current monitoring system uses a custom scheduler rather than Celery for the primary monitoring workflow.

The scheduler organizes monitors according to their configured intervals and performs recurring health checks.

Celery infrastructure exists in the project and may be used more extensively as the system grows.

The intention is to eventually support a more distributed background-job architecture when the monitoring workload justifies it.

---

## Testing

The project uses **pytest** for automated testing.

Tests are located under:

```text
tests/
```

and domain-specific tests are also maintained alongside the uptime monitoring module.

Run the test suite with:

```bash
pytest
```

---

## Deployment

The backend is containerized with Docker and deployed on **Render**.

The production architecture uses the containerized FastAPI backend together with its supporting PostgreSQL and Redis infrastructure.

---

## Related Repositories

Tavdev Monitor is part of the broader TAV DEV ecosystem.

The frontend is maintained separately within the Tavdev Monitor monorepo.

The scraping/toolbox code that originally existed alongside this project is being separated into its own project so that Tavdev Monitor can remain focused on uptime and API monitoring.

---

## Current Status

Tavdev Monitor is an actively developed project.

The core monitoring functionality currently supports:

* Account creation
* Authentication
* Instant URL health checks
* Recurring URL monitoring
* 1/2/5/10 minute intervals
* Redis-backed monitor scheduling
* 24-hour monitoring history
* Incident tracking
* JSON/CSV/Excel exports
* Docker deployment

Future infrastructure improvements may include broader Celery adoption and additional monitoring integrations.

---

## Author

**Md Abdullah All Mamun**

GitHub: https://github.com/mamun700263

Built under **TAV DEV**.
