# a11yTrack — project notes

Working notes kept alongside the code so that anyone (or any assistant) picking
up the project has the fixed decisions in one place. The reasoning behind each
decision is in `DECISIONS.md`; this file only states what is locked.

## What this is
An accessibility issue tracker built for a full-stack internship take-home.
Two seeded users sign in, create, view and edit their own WCAG issues, move
them through a status workflow, and see a log of every status change. The
app must be fully usable keyboard-only and with a screen reader (WCAG 2.2 AA
basics). Accessibility is the product being graded, not the CRUD.

## Stack (locked)
- Python 3.11+, Flask, Jinja2, Flask-SQLAlchemy, SQLite locally / PostgreSQL
  in the production design
- Hand-written backend validation (`app/validation.py`), no form library
- Signed session cookie, two seeded users, "sign in as" picker, no passwords
- pytest + Flask test client, in-memory SQLite per test
- Diagrams: Mermaid sources in `docs/*.mmd`, PNGs exported from the Mermaid
  Live Editor
- One small script in the whole app (status-message re-announce in `base.html`)

## Domain model (locked)
- `users` — id, display_name
- `issues` — id, owner_id (FK users), title (required), description, page_url
  (required, http/https), wcag_criterion, severity (Minor | Moderate | Serious |
  Critical), status, version (optimistic lock), created_at, updated_at.
  Index `(owner_id, created_at)` for the list page.
- `status_changes` — id, issue_id (FK), changed_by (FK users), from_status,
  to_status, changed_at. Index `(issue_id, changed_at)` for the history table.
  Written in the same transaction as the status update. Creation is not logged.
- Production-only (on the ER diagram, not built): `teams`, `users.team_id`,
  `users.email`, `issues.team_id`, `attachments` (with `alt_text`).

## Status workflow (locked)
```
Open -> In Progress -> Fixed -> Verified -> Closed
Fixed -> Reopened,  Verified -> Reopened,  Reopened -> In Progress
```
`ALLOWED_TRANSITIONS` in `app/workflow.py` is the only place the rules live.
Blocked example: Open -> Closed. Closed is final. The backend rejects any
transition not in the map with HTTP 400 and a sentence naming the allowed
targets.

## Ownership rule
Every per-issue route goes through `get_owned_issue_or_404()`, which filters by
id **and** owner_id. Not found and not owned both return 404, never 403, so the
existence of another user's issue is not leaked.

## Concurrency rule
Optimistic locking. Forms carry `version`; writes are
`UPDATE ... WHERE id=? AND owner_id=? AND version=?`. Zero rows affected means
someone saved first: rollback and HTTP 409 with a reload message.

## Error and message contract
- Validation: `validate_issue()` returns `{field: message}`; templates render
  the message next to the field (`aria-describedby`, `aria-invalid`) and in a
  focused summary with a "There is a problem" heading. Page title gets an
  "Error:" prefix.
- Workflow and conflict errors: one sentence, HTTP 400 / 409, same summary.
- Success: Flask `flash()` into a `role="status" aria-live="assertive"` region
  at the top of `<main>`, announced without moving focus.

## Repo layout
```
app/              __init__.py, models.py, routes.py, workflow.py, validation.py
app/templates/    base.html, login.html, issues_list.html, issue_form.html,
                  issue_detail.html, error.html
app/static/       style.css
tests/            conftest.py, helpers.py, test_workflow.py, test_ownership.py,
                  test_validation.py, test_notifications.py
docs/             architecture.mmd/.png, er.mmd/.png, workflow.mmd/.png
seed.py, run.py, requirements.txt
README.md  ARCHITECTURE.md  ACCESSIBILITY.md  DECISIONS.md  IMPROVEMENTS.md
```

## Run and test
```
python -m venv .venv && .venv\Scripts\activate    (Windows)
pip install -r requirements.txt
python seed.py          # drops and recreates instance/a11ytrack.sqlite3
python run.py           # http://127.0.0.1:5000
python -m pytest -q
```

## Pointers
- Why each choice was made: `DECISIONS.md` (append-only, dated)
- Production design and diagrams: `ARCHITECTURE.md`
- Keyboard, axe, Lighthouse and NVDA findings: `ACCESSIBILITY.md`
- Backlog: `IMPROVEMENTS.md`
