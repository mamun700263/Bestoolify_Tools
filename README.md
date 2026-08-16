# Tavdev Monitor

### Your uptime keeper.

Monitor websites and APIs, track their availability, and know when they're up or down.

Just add a URL or API endpoint, choose a monitoring interval, and let Tavdev Monitor handle the rest.

**Live:** https://monitor.tavdev.com

---

## What can you do with Tavdev Monitor?

### 🔎 Monitor Websites & APIs

Add any URL or API endpoint you want to keep track of.

* Set a custom monitoring interval
* Track uptime and response status
* Monitor API endpoints
* View historical monitoring data
* Download monitoring data

### ⚡ Instant URL Testing

You can also use Tavdev Monitor as a lightweight alternative to tools like `curl` or Postman when you just want to quickly test an endpoint.

**Try it:** https://monitor.tavdev.com/test

Paste a URL and instantly inspect its response.

---

## Architecture

Tavdev Monitor is built as a monorepo containing separate frontend and backend applications.

```text
Tavdev_tools/
├── backend/       # FastAPI backend
├── frontend/      # Next.js frontend
└── README.md      # Project overview
```

### Backend

* Python
* FastAPI
* Redis
* PostgreSQL

Backend documentation:

**[Backend README](backend/README.md)**

### Frontend

* Next.js

Frontend documentation:

**[Frontend README](frontend/README.md)**

---

## Deployment

| Component | Platform   |
| --------- | ---------- |
| Backend   | Render     |
| Frontend  | Vercel     |
| Database  | PostgreSQL |

---

## Repository

This repository contains the complete Tavdev Monitor application in a single monorepo.

* **Backend:** `backend/`
* **Frontend:** `frontend/`

---

## Contributor

* [Md Abdullah All Mamun](https://github.com/mamun700263)

---

## Tavdev

Built by **TAV DEV**.

**Monitor it. Track it. Know when it's up.**
