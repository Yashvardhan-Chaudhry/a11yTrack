# a11yTrack

Accessibility issue tracker: log WCAG issues found on web pages, move them
through a workflow, and keep a log of every status change. Built for the
Unified Accessibility full-stack intern take-home.

> Work in progress. Edit, status workflow, status log, tests and the full
> accessibility pass are not in yet; see "Known limitations" below.

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

## Known limitations (current build)

- Issues can be created and listed, but not yet edited or moved between statuses.
- The status log table is seeded but not yet shown.
- Tests, ARCHITECTURE.md and ACCESSIBILITY.md are still to come.
