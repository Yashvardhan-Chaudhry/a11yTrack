# IMPROVEMENTS.md — a11yTrack

Backlog / nice-to-haves. Not required for submission.
- Try `aria-live="polite"` on the status region with the same 1 s re-attach. The original failure was a 150 ms update colliding with page-title speech; at 1 s polite may announce. If NVDA speaks it, switch and drop the "assertive" limitation in ACCESSIBILITY.md.
- CSRF tokens on every POST form (Flask-WTF `CSRFProtect` or a hand-rolled per-session token). The session cookie is `SameSite=Lax` by default, which blocks cross-site POSTs in current browsers, but a token is the standard belt-and-braces.
- Pagination on the issue list. Locally the query is unbounded; production needs `LIMIT/OFFSET` or keyset pagination on `(created_at, id)` under the `ix_issues_owner_created` index.
