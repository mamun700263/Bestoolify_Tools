# Bestoolify Tools

> A scalable backend suite for scraping Google Maps using FastAPI, Celery, Redis, and Playwright.

## 🚀 Overview

Bestoolify Tools is designed for reliable, asynchronous web scraping and data export:

- Accepts scraping jobs via HTTP APIs
- Processes tasks asynchronously with Celery workers
- Scrapes Google Maps search results using Playwright
- Exports results in CSV or JSON formats
- Supports real-world deployment with Docker

---

## 🧰 Tech Stack

- **Python 3.12**
- **FastAPI** – API endpoints
- **Celery** – Background task processing
- **Redis** – Message broker & result backend
- **Playwright** – Browser automation
- **Docker & Docker Compose** – Development and deployment
- **Alembic** – Database migrations

---

## 📦 Features

- REST API to enqueue scraping jobs
- Dynamic query scraping
- Multiple export formats (CSV / JSON)
- Logging and monitoring via Flower dashboard
- Modular, testable, and production-ready code

---

## 📁 Repository Structure

```text
backend/
├── app/
│   ├── core/                # Core components (Celery config, logging, exporters)
│   ├── db/                  # Database setup
│   ├── scrapers/            # Scraper logic (Google Maps)
│   └── tasks/               # Celery task definitions
├── Dockerfile               # FastAPI Docker image
├── Dockerfile-celery        # Celery worker Docker image
├── docker-compose.yml       # Development orchestration
├── requirements.txt
├── README.md
└── tests/                   # Unit tests
````

---

## 🛠️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/mamun700263/Bestoolify_Tools.git
cd Bestoolify_Tools/backend
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
```

### 4. Run the development stack

```bash
docker compose up --build
```

This starts:

* FastAPI at `http://localhost:8000`
* Redis message broker
* Celery worker
* Flower monitoring dashboard at `http://localhost:5555`

---

## 📡 Deployment

For production, deploy services independently:

1. **FastAPI** as the main web service
2. **Celery Worker** for background tasks
3. **Redis** as a managed instance
4. **Flower** (optional) for monitoring

Use platforms like **Render**, **Railway**, or a VPS to host each service.

---

## 📌 API Examples

### Start a scrape job

```
POST /google_map_scrapper/run?target=shoes+stores&file_type=csv
```

### Check task status

```
GET /google_map_scrapper/status/{task_id}
```

---

## 🧪 Testing

Run unit tests:

```bash
pytest tests/
```

---

## 📜 License

MIT License

---

## 🖼️ Architecture Diagram (Optional)

```
[ FastAPI API ] --> [ Celery Worker ] --> [ Playwright Scraper ] --> [ CSV / JSON Export ]
                           |
                           v
                        [ Redis ]
```

---

## ⚡ Notes for Contributors

* Use virtual environments
* Follow PEP8 coding standards
* Maintain modularity for tasks and scrapers
* Document all new endpoints or exporters


