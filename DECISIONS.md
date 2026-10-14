# DECISIONS.md — a11yTrack

Append-only. One line per decision + why. Newest at bottom.

- 2026-10-14 — Name: a11yTrack. "a11y" is industry shorthand for accessibility; signals domain fluency to reviewers.
- 2026-10-14 — Backend: Flask. Smallest surface; server-rendered forms make WCAG basics nearly free. Alt considered: FastAPI — better pure API, but would push toward an SPA and custom focus management.
- 2026-10-14 — Templates: Jinja2. Flask default; interviewer mentioned it.
- 2026-10-14 — Server-rendered pages, no SPA. Native `<form>`, `<table>`, `<select>` satisfy keyboard/focus/label criteria by default; a client-routed SPA would need manual title updates, live regions, focus moves.
- 2026-10-14 — DB access: Flask-SQLAlchemy. Same model code runs on SQLite locally and PostgreSQL in production, so Part 1 and Part 2 stay consistent. Alt: raw sqlite3 — simpler but makes the prod story hand-wavy.
- 2026-10-14 — DB: SQLite local, PostgreSQL in production design. Brief allows SQLite; Postgres handles 20k users + concurrent writes + row-level locking.
- 2026-10-14 — Auth: Flask session cookie + two seeded users + "sign in as" picker. Brief forbids real auth; keeps login trivially keyboard-accessible.
- 2026-10-14 — Validation: hand-written `validate_issue()` returning `{field: message}`. Explainable on the call; no library behaviour to defend. Alt: WTForms — faster, more magic.
- 2026-10-14 — Error contract: validation errors returned as `{field: message}` dict; templates render inline error + error summary at top; focus moves to summary. This is the "where errors come from" answer for brief §8.
- 2026-10-14 — Status workflow: Open → In Progress → Fixed → Verified → Closed; Fixed/Verified → Reopened → In Progress. Blocked example: Open → Closed. Encoded as a single `ALLOWED_TRANSITIONS` dict in `workflow.py`; backend rejects with 400.
- 2026-10-14 — Ownership: every issue query scoped by `owner_id`; unowned returns 404 not 403, so existence of other users' issues is not leaked.
- 2026-10-14 — Concurrency: optimistic locking via `version` column; stale write → 409 with reload message. Covers same-user-two-tabs locally and team-shared issues in production. Assumption to document: production issues are team-scoped.
- 2026-10-14 — Status log: separate `status_changes` table (who, when, from, to), written in the same DB transaction as the status update. Never derived from `updated_at`.
- 2026-10-14 — WCAG criterion input: native `<input list=...>` + `<datalist>` of WCAG 2.2 criteria. Brief says "chosen from a list or typed"; datalist does both with zero custom JS.
- 2026-10-14 — Diagrams: Mermaid, exported to PNG. Text-based, lives in repo, editable live on the call, explicitly allowed by brief. Avoided Excalidraw (sketch aesthetic reads as hand-drawn).
- 2026-10-14 — AI use: Claude Code drafts code and Mermaid; every file read and edited by me before commit. Disclosed in README AI note.
- 2026-10-14 — Tests: pytest + Flask test client, in-memory SQLite per test. Minimum: invalid transition → 400; cross-user GET/POST → 404; required-field validation.
- 2026-10-14 — Critical-issue email (brief §7): production-only, via queue + worker so the request returns immediately. Local build logs a line instead. Marked production-only on the architecture diagram.
