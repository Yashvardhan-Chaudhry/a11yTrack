# a11yTrack

Accessibility issue tracker: log WCAG issues found on web pages, move them
through a workflow, and keep a log of every status change. Built for the
Unified Accessibility full-stack intern take-home.

> Work in progress. The accessibility pass, ARCHITECTURE.md and
> ACCESSIBILITY.md are still to come; see "Known limitations" below.

## Run locally

Requires Python 3.11+.

```
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python seed.py                  # creates instance/a11ytrack.sqlite3 with demo data
python run.py                   # http://127.0.0.1:5000
```

`seed.py` drops and recreates all tables, so run it again any time you want a
clean demo database.

## Demo accounts

No passwords. Pick a user on the sign-in page:

| User | Seeded issues |
|---|---|
| Asha Rao | 4 |
| Ben Okafor | 4 |

Each user sees only their own issues.

## Run the tests

```
python -m pytest -q
```

Tests run against an in-memory SQLite database and cover: an invalid status
change is rejected with 400 and not logged; one user is blocked (404) from
another user's issue on every route; backend validation; the optimistic-lock
409 on stale edits and status changes.

## Status workflow

```
Open -> In Progress -> Fixed -> Verified -> Closed
Fixed -> Reopened, Verified -> Reopened, Reopened -> In Progress
```

Closed is final. The detail page only offers allowed next statuses, and the
backend rejects anything else (for example Open -> Closed) with HTTP 400.

## Known limitations (current build)

- Accessibility self-check (keyboard pass, axe, NVDA) not yet recorded.
- ARCHITECTURE.md and ACCESSIBILITY.md not yet written.
