# a11yTrack

An accessibility issue tracker: log WCAG issues found on web pages, move each
one through a status workflow, and keep a log of every status change. Built
for the Unified Accessibility full-stack intern take-home. The app is designed
to be used keyboard-only and with a screen reader; see `ACCESSIBILITY.md` for
what was checked.

## Run locally

Requires Python 3.11 or newer. Everything runs on your machine with free tools;
nothing is hosted.

Windows:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python run.py
```

macOS / Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py
python run.py
```

Then open http://127.0.0.1:5000.

`seed.py` creates `instance/a11ytrack.sqlite3` with two demo users and eight
issues. It drops and recreates all tables, so run it again whenever you want a
clean database. Data persists across restarts of `run.py`.

## Demo accounts

No passwords. Pick a user on the sign-in page.

| User | Seeded issues |
|---|---|
| Asha Rao | 4 |
| Ben Okafor | 4 |

Each user sees only their own issues. Typing another user's issue URL, or
posting to it directly, returns 404.

## Run the tests

```
python -m pytest -q
```

31 tests run against an in-memory SQLite database. They cover:

- an invalid status change (for example Open to Closed) is rejected with 400
  and nothing is written to the status log;
- one user is blocked from another user's issue on every route, by GET and by
  POST, with 404;
- backend validation of every field, with the typed values kept on error;
- the optimistic-lock 409 on stale edits and stale status changes;
- the Critical-issue notification hook (a log line locally).

## What is where

| Path | Purpose |
|---|---|
| `app/routes.py` | All endpoints, the ownership gate, the optimistic lock |
| `app/workflow.py` | `ALLOWED_TRANSITIONS`, the only place the workflow lives |
| `app/validation.py` | Backend validation returning `{field: message}` |
| `app/models.py` | `users`, `issues`, `status_changes` and their indexes |
| `app/templates/` | Server-rendered pages; `base.html` has the skip link and live region |
| `app/static/style.css` | Styles, focus indicator, contrast tokens |
| `tests/` | pytest suite |
| `docs/` | Mermaid sources and exported PNGs for the three diagrams |
| `ARCHITECTURE.md` | Part 1: production design, request flows, data model, API, scale |
| `ACCESSIBILITY.md` | Keyboard pass, axe and Lighthouse results, NVDA findings, remaining issues |
| `DECISIONS.md` | Every design decision with its reason, in the order made |
| `IMPROVEMENTS.md` | Backlog of things I would do next |
| `claude.md` | Locked project facts kept beside the code |

## Status workflow

| From | Allowed to |
|---|---|
| Open | In Progress |
| In Progress | Fixed |
| Fixed | Verified, Reopened |
| Verified | Closed, Reopened |
| Reopened | In Progress |
| Closed | none, final |

The detail page shows one button per allowed next status. The backend checks
every change against the same table and rejects anything else with HTTP 400
and a message naming the allowed targets. Every accepted change is written to
`status_changes` with who, when, from and to, in the same transaction as the
update, and shown on the issue page.

## Assumptions

- Issues belong to the user who created them. Teams and shared issues are part
  of the production design only (`ARCHITECTURE.md`, section 3).
- Creating an issue is not a status change, so it does not appear in the log;
  the issue's created time records it.
- Closed is final. A regression on a closed issue is a new issue.
- The WCAG criterion field offers the WCAG 2.2 A and AA criteria in a native
  `datalist` and also accepts free text, as the brief allows either.
- Times are stored and shown in UTC.

## Known limitations

- No CSRF token on the forms. Browsers treat the session cookie as
  `SameSite=Lax` by default, which blocks cross-site POSTs, but a token is the
  standard second layer.
- The issue list is not paginated. Fine for the seeded data; production needs
  keyset pagination (`ARCHITECTURE.md`, section 6).
- No handler for a database outage; the exception surfaces as a plain 500.
- The `SECRET_KEY` is a fixed development value in `app/__init__.py`.
- SQLite allows one writer at a time; the production design uses PostgreSQL.
- Attachments, teams and the team-lead email are designed, not built. Locally
  a Critical issue only writes a log line.
- The status message live region is `assertive`, which interrupts the screen
  reader; acceptable because it is the only live region and fires once per page.
- Accessibility was tested with NVDA and Chrome on Windows only. Not tested
  with JAWS, VoiceOver or Firefox.

## Accessibility summary

Every page works keyboard-only with a visible two-ring focus indicator, a skip
link, one `h1`, per-page titles and native controls. Errors are inline and in a
focused summary; success messages are announced without moving focus. axe
reports 0 violations on 16 page states and Lighthouse scores 100 on every page
tested. Full findings, including what NVDA surfaced and what was changed as a
result, are in `ACCESSIBILITY.md`.

## AI note

I used Claude Code as a pair programmer during this assignment: it helped
write code, tests and first drafts of the documentation and of the Mermaid
diagram text, and it ran the axe checks. The design decisions recorded in
`DECISIONS.md`, the final diagrams (laid out and exported in the Mermaid Live
Editor), the keyboard and NVDA testing, and all review and editing are mine.
I read and understand every file in this repository and can explain and change
any part of it.
