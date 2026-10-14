# a11yTrack — claude.md

Source of truth for this project. If anything elsewhere (chat, memory, notes)
disagrees with this file, this file wins.

## What this is
Take-home assignment for a full-stack internship at Unified Accessibility.
An accessibility issue tracker: two seeded users log in, create/view/edit
their own WCAG issues, move them through a status workflow, and see a log
of every status change. Must be fully usable keyboard-only and with a
screen reader (WCAG 2.2 AA basics). The accessibility is the product being
graded, not the CRUD.

Brief: `docs/brief.pdf` (treat as the spec). Reviewers: Archit Mittal +
two CC'd colleagues. Review call follows submission — every decision must
be explainable live.

## Hard deadline
**Thursday 15 Oct 2026, 22:00 IST.**
Target submit: 19:00 IST. Hard stop: 21:30 IST.
Submit = reply to Archit's email with the repo link (reviewer access granted).

## Deliverables (all required)
| File | Purpose | Status |
|---|---|---|
| `README.md` | Setup, run, demo accounts, run tests, assumptions, known limitations, AI note | todo |
| `ARCHITECTURE.md` | Part 1 — 9 sections + 3 Mermaid diagrams (PNG exported, tool named) | todo |
| `ACCESSIBILITY.md` | Keyboard pass, automated check (axe/Lighthouse), NVDA notes, remaining issues | todo |
| `tests/` | ≥2 meaningful: invalid transition rejected; cross-user access blocked | done |
| App | Flask + Jinja2 + SQLAlchemy + SQLite, runs locally | done (a11y pass pending) |

## Stack (locked — see DECISIONS.md for why)
- Python 3.x, Flask, Jinja2, Flask-SQLAlchemy, SQLite (dev) / PostgreSQL (prod design)
- Hand-written backend validation (no WTForms)
- Session-cookie auth, two seeded users, "sign in as" picker
- pytest + Flask test client
- Diagrams: Mermaid, exported to PNG
- Windows dev machine; NVDA for screen-reader check

## Domain model (locked)
- `users` — id, display_name
- `issues` — id, owner_id (FK users), title (req), description, page_url
  (req, http/https), wcag_criterion, severity (Minor|Moderate|Serious|Critical),
  status, version (optimistic lock), created_at, updated_at
- `status_changes` — id, issue_id (FK), changed_by (FK users),
  from_status, to_status, changed_at
- Production-only (on the ER diagram, not built locally): `teams` (id, name,
  lead_user_id), `users.team_id`, `users.email`, `issues.team_id`,
  `attachments` (id, issue_id, storage_key, uploaded_by, created_at).

## Status workflow (locked)
```
Open → In Progress → Fixed → Verified → Closed
Fixed → Reopened,  Verified → Reopened,  Reopened → In Progress
```
Blocked example to cite: `Open → Closed` (nothing closes without Fixed + Verified).
Backend rejects any transition not in the allowed map with HTTP 400 + message.

## Ownership rule
Every issue route loads `Issue.query.filter_by(id=..., owner_id=current_user.id)`.
Not found OR not owned → 404 (never 403, to avoid leaking existence).

## Concurrency
Optimistic locking: forms carry `version`; `UPDATE ... WHERE id=? AND version=?`;
0 rows → 409 "This issue was changed since you loaded it — reload."

## Repo layout (target)
```
a11ytrack/
  app/            __init__.py, models.py, routes.py, workflow.py, validation.py
  app/templates/  base.html, login.html, issues_list.html, issue_form.html, issue_detail.html, error.html
  app/static/     style.css
  tests/          test_workflow.py, test_ownership.py, test_validation.py
  docs/           architecture.mmd, er.mmd, workflow.mmd + exported .png, brief.pdf
  seed.py, run.py, requirements.txt
  README.md ARCHITECTURE.md ACCESSIBILITY.md DECISIONS.md IMPROVEMENTS.md claude.md
```

## Local tooling (verified working)
- Python 3.14 venv at `.venv` → `.venv\Scripts\activate`, `python run.py`
- axe CLI: `axe http://127.0.0.1:5000/path --chromedriver-path "C:/Users/chaud/.cache/puppeteer/chromedriver/win64-154.0.8037.57/chromedriver-win64/chromedriver.exe" --chrome-options="headless,no-sandbox"`
  (bundled chromedriver is 155, Chrome is 154 — hence the explicit path)
- NVDA 2026.2 at `C:\Program Files\NVDA\nvda.exe` (winget); Lighthouse via Chrome DevTools

## Current state
- Slice 1 + 2 done: models, seed, sign-in, list + filters, create, detail page
  (fields, one status-change button per allowed target, status history table),
  edit (no status field), `ALLOWED_TRANSITIONS` in workflow.py with 400 on
  rejection, status_changes written in the same transaction, ownership via
  `get_owned_issue_or_404()` (404 never 403), optimistic lock -> 409 on edit
  and status change, titled `error.html` for 404s, pytest suite in `tests/`.
- Not yet: accessibility pass, ARCHITECTURE.md, ACCESSIBILITY.md, final README.

## Planner (revised 18:40 Wed; ~2h behind original)
| Slot | Task | Done when |
|---|---|---|
| Wed 18:45–19:30 | `git init`, venv, requirements, skeleton files, commit | app runs, shows "hello" |
| 19:30–20:00 | Mermaid v1 (3 diagrams) → `docs/*.png` | 3 PNGs render, arrows labelled |
| 20:00–22:30 | Models + seed + login + issue create/list/edit + filters + backend validation | create → list → edit works in browser |
| 22:30–23:15 | Workflow + status log + ownership + optimistic lock | invalid transition → 400; other user's id → 404 |
| 23:15 | HANDOFF block into this file. Stop. | state saved |
| Thu 09:00–10:30 | Tests (2 required + validation + log) | pytest green |
| 10:30–12:30 | Accessibility pass (skip link, labels, error summary+focus, live region, titles, contrast, 320px/200%) | full keyboard-only pass |
| 12:30–13:30 | Break / class buffer (class is 2h — slot it here or shift blocks below) | — |
| 13:30–14:30 | axe/Lighthouse + NVDA, write ACCESSIBILITY.md | findings recorded |
| 14:30–16:30 | ARCHITECTURE.md sections 1–9, diagrams reconciled with real code | diagrams match shipped app |
| 16:30–17:30 | README + AI note; fresh-clone test in a new folder | stranger can run it |
| 17:30–18:30 | Review-call prep — explain every DECISIONS.md line aloud | — |
| 18:30–19:00 | Push, verify access, reply email | submitted |

## Next steps
1. Initialise repo and skeleton (first Claude Code prompt).
2. Mermaid diagrams v1.
3. Build core app per planner.

## Open threads
- ~~Reviewers' GitHub handles~~ — resolved: repo is public at https://github.com/Yashvardhan-Chaudhry/a11yTrack
- Thursday 2h class time not yet slotted — place it, shift blocks.
- Severity → "notify team lead" email (brief §7) is production-only; local = log line. Confirm in ARCHITECTURE.md.

## Pointers
- Why each choice: see `DECISIONS.md`
- Backlog / nice-to-haves: see `IMPROVEMENTS.md`
- How it's built: see `ARCHITECTURE.md` (this doubles as the Part 1 deliverable)
