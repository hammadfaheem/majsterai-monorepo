# MajsterAI Application Overview

This document explains how the whole MajsterAI application works end-to-end: auth, organizations, leads, calls, appointments, services, invoices, agent configuration, and platform admin. Payment integration is out of scope here and will be added later.

---

## 1. Purpose and scope

**What MajsterAI is:** A voice AI agent platform with a CRM-style dashboard. You can:

- Manage **organizations** and **team members** (with roles and time off).
- Manage **leads** (contacts) with notes, activities, and tasks.
- View **call history** and transcripts from voice AI calls (LiveKit).
- Manage **appointments**, **schedules**, **departments**, and **availability**.
- Define **services** (trade categories and trade services) and **invoices** (header-only; no payment capture yet).
- Configure the **AI agent** (prompt, variables), **scenarios**, and **transfers** for voice flows.
- Use **tags** (tag bases) and **tasks** across the org.
- Use **reminders**, **lead addresses**, and **notifications** (APIs exist; limited UI).

**Who uses it:**

- **Org members:** Users belong to one or more organizations with a role per org: **owner**, **admin**, or **member**. They see only data for organizations they belong to.
- **Platform superadmins:** Users with platform role **SUPERADMIN** can access the Admin area (all organizations and all users) and see every org in the switcher.

**Out of scope in this doc:** Payment integration (Stripe, invoice payments, “Pay now”) is to be added later.

---

## 2. High-level architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser – Dashboard (React + Vite)                              │
│  apps/dashboard                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP + JWT
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Backend – apps/api                                      │
│  Auth, orgs, leads, calls, appointments, services, invoices,     │
│  agent, scenarios, transfers, admin, etc.                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌──────────────────────┐    ┌──────────────────────┐
│  PostgreSQL          │    │  LiveKit Cloud       │
│  (Docker)            │    │  (voice / WebRTC)    │
│  All app data        │    │  Used by Test Agent  │
└──────────────────────┘    └──────────────────────┘
```

- **Monorepo:** `apps/api` (FastAPI), `apps/dashboard` (React + Vite). Optional: `majsterai-agent` (separate repo) joins LiveKit rooms and runs the voice agent.
- **Database:** PostgreSQL started via `docker compose up -d postgres`; schema and migrations in `apps/api/src/db/` and `apps/api/alembic/`.
- **Auth:** JWT issued on login/register; dashboard stores the token in `localStorage` and sends it as `Authorization: Bearer <token>`; API uses it to resolve the current user and (optionally) enforce SUPERADMIN.

---

## 3. Auth and users

**Flow:**

1. **Register:** POST `/api/auth/register` (email, name, password) → user created → JWT + user returned.
2. **Login:** POST `/api/auth/login` (email, password) → JWT + user (id, email, name, **role**) returned.
3. **On load:** If the dashboard has a token but no user in state, it calls GET `/api/auth/me` to restore the user (including **role**).

**User roles:**

- **Platform-level** (stored on the user): **SUPERADMIN**, **STAFF**, **CUSTOMER**. Only SUPERADMIN can access `/admin` and see all organizations.
- **Org-level** (stored on membership): **owner**, **admin**, **member**. Used for team management; frontend does not yet enforce these for hiding Settings/Team.

**Superadmin:** Set `SUPERADMIN_EMAIL=<email>` in the API `.env`. On startup, the API finds that user and sets `role = 'SUPERADMIN'`. That user then logs in with their normal password and sees the Admin link and all orgs.

---

## 4. Organizations and members

**Organizations:** Each org has name, timezone, country, currency, default_schedule_id, tag, seats, etc. (see Settings page).

**List organizations:**

- **SUPERADMIN:** GET `/api/organizations` returns all organizations.
- **Others:** Returns only organizations where the current user has a membership.

The dashboard shows an org switcher; all main data (leads, calls, appointments, etc.) is scoped by the **current organization** selected there.

**Members:** Per org, you can list members (GET `/api/memberships/{org_id}`), add (user_id, role), update role, and remove. **Time off** is managed via membership unavailability: list, create, update, delete date ranges (used on the Team page).

---

## 5. Leads and lead center

**Leads:** List (with status filter), create, get one, update. Each lead has name, email, phone, status, source, etc.

**Lead detail page** (`/leads/:id`):

- **Profile:** View and edit (name, email, phone, status, source).
- **Timeline:** Notes and activities (from GET `/api/leads/{id}/notes` and `/api/leads/{id}/activities`). You can add a note or log an activity from the UI.
- **Tasks:** Tasks for this lead (filtered by lead_id); create task, mark complete.

**Notes and activities** are stored per lead and shown in chronological order. There is no lead–tag linking or inquiry timeline in the current implementation (optional / future).

---

## 6. Calls and call history

**Call history:** List by org, get by room name (with transcript and summary), analytics (counts, duration). The dashboard has a status filter and a detail modal showing transcript and summary.

**Flow:**

1. Test Agent (or another client) creates a LiveKit room via the API.
2. The voice agent (e.g. majsterai-agent) joins the room and runs the conversation.
3. Call metadata is written to **call_history**; transcript (if generated) is stored separately.
4. The dashboard shows the list and, on row click, the detail (transcript/summary).

---

## 7. Appointments, schedules, departments

**Appointments:** List, create (lead, optional service, start/end), update, cancel. There is no UI for **appointment assignees** yet (the `appointment_assignee` table exists in the DB).

**Schedules:** List, create, update, delete. Fields: name, time_zone, optional department_id.

**Departments:** List by org, create, update, delete. Fields: name, description, default_schedule_id, is_active, max_concurrent_calls, escalation_timeout, etc.

**Availability:** CRUD by schedule or org (when a user is available). Used for scheduling logic; APIs under `/api/availabilities`.

---

## 8. Services and invoicing

**Services:**

- **Trade categories:** e.g. Plumbing, Electrical; full CRUD in the dashboard.
- **Trade services:** Name, description, duration, pricing, category, is_active; full CRUD.

**Invoices:** List, create, edit (header: lead, status, date, due_date, reference, notes), delete. There are **no line items** in the current API/UI. There is **no payment capture**; you can set status to “paid” in the edit modal as a simple “Mark as paid” (a dedicated one-click button is optional later).

---

## 9. Agent, scenarios, transfers

**Agent:** One agent per org. The dashboard loads it (GET `/api/agents/{org_id}`) and can edit name, prompt, extra_prompt, variables. This config is used by LiveKit / the voice agent for behavior.

**Scenarios:** Conversation flows: name, prompt, response, trigger_type, trigger_value, is_active. Full CRUD in the dashboard.

**Transfers:** Call transfer rules: label, method (COLD/WARM), destination_type, destination, summary_format. Full CRUD in the dashboard.

---

## 10. Tags and tasks

**Tags (tag_bases):** Org-level definitions: value, color, type (LEAD/INQUIRY). Full CRUD in the dashboard. They are **not** yet attachable to leads in the API/UI (optional / future).

**Tasks:** List (filter by lead, assignee, complete), create (title, optional lead, optional assignee), update (e.g. mark complete), delete. Used on the Tasks page and on the lead detail page.

---

## 11. Reminders, lead addresses, notifications

**Reminders:** CRUD; linked to a lead or appointment; fields include datetime, notes, type, priority. APIs under `/api/reminders`.

**Lead addresses:** CRUD per lead (for location / modality). APIs under `/api/lead-addresses`.

**Notifications:** notification_type (GET/PUT), org_notification_recipient (GET/PUT), notification_log (GET). There is no Settings UI for notification preferences yet (optional).

---

## 12. Platform admin

**Who:** A user with `role === 'SUPERADMIN'` (set via `SUPERADMIN_EMAIL` in API `.env` at startup).

**What:** The Admin area in the dashboard:

- **Organizations:** List all orgs, edit any org (name, timezone, country, currency, default_schedule_id, tag, seats).
- **Users:** List all users, edit platform role (SUPERADMIN / STAFF / CUSTOMER).

**API:** All under `/api/admin/*` (e.g. GET/PUT `/api/admin/organizations`, GET/PUT `/api/admin/organizations/{id}`, GET/PATCH `/api/admin/users/{id}`). Every admin endpoint is protected by `require_superadmin`.

**Visibility:** The “Admin” sidebar link is shown only when `user?.role === 'SUPERADMIN'`. Non-superadmins who open `/admin` are redirected to the dashboard.

---

## 13. Data flow summary

| Flow | Steps |
|------|--------|
| **Login** | POST `/api/auth/login` → token + user (with role) → stored in frontend → token sent as `Authorization: Bearer` on every request; role used for Admin visibility and org list scope. |
| **Org scope** | GET `/api/organizations` returns only member orgs (or all for SUPERADMIN) → user picks current org → all main list/create/update calls use that `org_id`. |
| **Lead flow** | Create lead → open lead detail → add notes/activities → create tasks → optionally create appointments or invoices linked to the lead. |
| **Voice / calls** | Create LiveKit room via API → agent runs call → call_history + transcript stored → dashboard shows list and detail (Calls page and analytics). |

---

## 14. How to run and test

1. **Start PostgreSQL:** From the monorepo root, run `docker compose up -d postgres`. Ensure `.env` (or env) has `DATABASE_URL` matching the compose defaults (e.g. `postgresql://majsterai:majsterai_dev@localhost:5432/majsterai`).

2. **Run the API:** `cd apps/api && uvicorn src.main:app --reload --port 8000`. Set `apps/api/.env` (e.g. `DATABASE_URL`, `SUPERADMIN_EMAIL`). On startup, the API runs migrations (via `init_db`) and, if `SUPERADMIN_EMAIL` is set, grants that user the SUPERADMIN role.

3. **Run the dashboard:** `cd apps/dashboard && pnpm dev`. Set `VITE_API_BASE_URL=http://localhost:8000` (or your API URL) so the dashboard talks to the API.

4. **First superadmin:** Register a user in the dashboard (e.g. your email). Set `SUPERADMIN_EMAIL` to that email in `apps/api/.env`. Restart the API. Log in as that user; you should see the Admin link and (if you have multiple orgs) all organizations in the switcher.

5. **Basic testing:** Create an org (or use the one you’re in), add leads, add notes/activities and tasks on a lead, create appointments and invoices, configure the agent/scenarios/transfers, and (as superadmin) open Admin to manage orgs and user roles.

---

**Payment integration:** To be added later (Stripe, invoice payments, “Pay now” flows). The rest of the application is ready for testing without payment.
