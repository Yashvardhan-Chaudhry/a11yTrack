"""Status workflow. Pure data and functions, no Flask imports.

Open -> In Progress -> Fixed -> Verified -> Closed
Fixed -> Reopened, Verified -> Reopened, Reopened -> In Progress
Closed is terminal. Anything not in ALLOWED_TRANSITIONS is rejected by the
backend with HTTP 400 (see routes.issue_status).
"""

STATUSES = ("Open", "In Progress", "Fixed", "Verified", "Closed", "Reopened")

ALLOWED_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "Open": ("In Progress",),
    "In Progress": ("Fixed",),
    "Fixed": ("Verified", "Reopened"),
    "Verified": ("Closed", "Reopened"),
    "Reopened": ("In Progress",),
    "Closed": (),
}


def allowed_targets(status: str) -> tuple[str, ...]:
    """Statuses an issue may move to from `status`. Empty for terminal states."""
    return ALLOWED_TRANSITIONS.get(status, ())


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in allowed_targets(from_status)
