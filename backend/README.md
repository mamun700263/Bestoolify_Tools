# Playwrite Scraper Suite

**A production-grade FastAPI system for scraping Google Maps and exporting data asynchronously.**

---

## Features

- FastAPI REST endpoints for managing scraping tasks.
- Asynchronous task processing with Celery & Redis.
- Modular scrapers for Google Maps with resilient scrolling and extraction.
- Data exporters: CSV, JSON, Excel, Google Sheets.
- Dockerized deployment for each service: FastAPI, Celery, Redis, Flower.
- Logging & observability built-in.

---

## Tech Stack

- Python 3.12
- FastAPI, Pydantic, SQLAlchemy
- Celery, Redis
- Docker & Docker Compose
- Alembic for migrations
- Optional: Google Sheets API

---

## Setup / Installation

1. **Clone the repo**

```bash
git clone https://github.com/mamun700263/Bestoolify_Tools.git
cd backend