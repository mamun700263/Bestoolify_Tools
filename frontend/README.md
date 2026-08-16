# Tavdev Monitor — Frontend

The frontend application for **Tavdev Monitor**, a lightweight uptime and API monitoring platform for developers.

**Live application:** https://monitor.tavdev.com

The frontend provides the interface for creating monitors, testing URLs, viewing monitoring history, and managing user accounts.

---

## Tech Stack

* **Next.js 16**
* **React 19**
* **TypeScript**
* **Axios**
* **Zustand**
* **Tailwind CSS**
* **shadcn/ui**
* **Lucide React**
* **React Query**

The application uses the **Next.js App Router**.

---

## Features

### URL Testing

The `/test` page provides an instant URL health-check interface.

Users can enter a URL and inspect the response without creating an account.

This is intended as a lightweight developer-oriented alternative to reaching for `curl` or Postman for simple endpoint checks.

---

### Authentication

The application supports:

* Email/password registration
* Email/password login
* Google OAuth
* JWT authentication
* Access token refresh
* Persistent authentication state
* Account verification

Authenticated API requests automatically attach the current access token.

If an API request returns `401 Unauthorized`, the frontend attempts to refresh the access token and retry the original request.

---

## Authentication Flow

The authentication system is separated into several responsibilities.

```text
                        Application
                             │
                             ▼
                       AuthProvider
                             │
                             ▼
                       initAuth()
                             │
                             ▼
                       /accounts/me
                             │
                    ┌────────┴────────┐
                    │                 │
                  Valid            Invalid
                    │                 │
                    ▼                 ▼
              Zustand Store         Logout
                    │
                    ▼
                 UI State
```

### API Authentication

The Axios API client is responsible for authentication at the HTTP layer.

```text
Request
   │
   ▼
Attach access token
   │
   ▼
Backend
   │
   ├── 2xx ────────────────► Return response
   │
   └── 401
        │
        ▼
   Refresh access token
        │
        ▼
   Retry original request
```

A shared refresh promise prevents multiple concurrent `401` responses from triggering multiple refresh requests.

---

## Application Structure

```text
src/
├── app/
│   ├── (auth)/
│   │   ├── callback/
│   │   ├── login/
│   │   ├── register/
│   │   └── verify/
│   │
│   ├── dashboard/
│   │   └── monitors/
│   │
│   ├── leaderboard/
│   ├── pricing/
│   ├── profile/
│   ├── test/
│   ├── page.tsx
│   └── layout.tsx
│
├── components/
│   ├── auth/
│   ├── authprovider/
│   ├── buttons/
│   ├── landing/
│   ├── monitors/
│   └── ui/
│
├── lib/
│   ├── api.ts
│   ├── auth.ts
│   ├── authBootstrap.ts
│   └── utils.ts
│
└── store/
    └── auth.ts
```

### `app/`

Contains application routes using the Next.js App Router.

Major routes include:

| Route                      | Purpose                 |
| -------------------------- | ----------------------- |
| `/`                        | Landing page            |
| `/login`                   | User login              |
| `/register`                | Account registration    |
| `/verify`                  | Account verification    |
| `/callback`                | OAuth callback          |
| `/dashboard`               | Main dashboard          |
| `/dashboard/monitors`      | Monitor management      |
| `/dashboard/monitors/[id]` | Monitor details/history |
| `/test`                    | Instant URL testing     |
| `/pricing`                 | Pricing information     |
| `/leaderboard`             | Monitoring leaderboard  |
| `/profile`                 | User profile            |

---

## API Client

The central API client is located at:

```text
src/lib/api.ts
```

It uses Axios and provides:

* Configured API base URL
* Request authentication
* Access-token injection
* `401` detection
* Refresh-token handling
* Request retrying
* Forced logout when authentication can no longer be restored

The API base URL is configured through:

```text
NEXT_PUBLIC_API_URL
```

If no value is supplied during local development, the frontend falls back to:

```text
http://localhost:8000
```

---

## Client Authentication State

Authentication state is managed using **Zustand**.

The store maintains information such as:

```text
Account
Authentication status
Login state
Logout state
```

Authentication state is initialized when the application starts.

The frontend checks the existing access token and calls the backend's account endpoint to restore the authenticated account.

---

## Monitor Dashboard

Authenticated users can manage their monitoring targets through the dashboard.

The dashboard supports:

* Viewing monitors
* Creating monitors
* Updating monitors
* Deleting monitors
* Viewing monitor status
* Inspecting ping history
* Viewing monitoring information
* Downloading monitoring data

Each monitor has its own detail page.

```text
/dashboard
      │
      └── monitors
            │
            ├── Monitor list
            │
            └── [id]
                 └── Monitor details
```

---

## Data Export

The frontend provides a download interface for monitoring data.

Supported export formats include:

* JSON
* CSV
* Excel

The actual export processing is performed by the backend.

---

## Styling & UI

The application uses:

* Tailwind CSS
* shadcn/ui
* Radix UI
* Lucide icons

Reusable UI components are maintained under:

```text
src/components/ui/
```

Application-specific components are organized by feature, such as:

```text
src/components/auth/
src/components/landing/
src/components/monitors/
```

---

## Local Development

### Requirements

* Node.js
* npm
* Tavdev Monitor backend

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The application will run using the Next.js development server.

---

## Environment Variables

Create a local environment file and configure the backend API URL:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, this should point to the deployed Tavdev Monitor backend.

Do not commit secrets or environment files containing credentials.

---

## Available Scripts

```bash
npm run dev
```

Starts the development server.

```bash
npm run build
```

Creates a production build.

```bash
npm run start
```

Starts the production server.

```bash
npm run lint
```

Runs ESLint.

---

## Deployment

The frontend is deployed using **Vercel**.

The production frontend communicates with the deployed Tavdev Monitor backend through the configured API URL.

---

## Backend

The frontend depends on the Tavdev Monitor FastAPI backend.

The backend provides:

* Authentication
* Monitor management
* URL health checks
* Monitoring history
* Incident information
* Data exports

See the backend documentation for API and infrastructure details.

---

## Project Status

Tavdev Monitor is actively being developed.

Current frontend functionality includes:

* Public landing page
* Account registration and login
* Google OAuth
* Account verification
* Instant URL testing
* Authenticated dashboard
* Monitor management
* Monitor detail pages
* Monitoring history
* Data export
* User profile
* Pricing page
* Leaderboard

---

## Author

**Md Abdullah All Mamun**

GitHub: https://github.com/mamun700263

Built under **TAV DEV**.
