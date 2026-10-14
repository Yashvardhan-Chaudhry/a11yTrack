"""Small helpers shared by the test modules."""
from app.models import Issue

ALICE, BOB = 1, 2  # ids assigned by conftest in insertion order
ALICE_ISSUE, BOB_ISSUE = 1, 2

VALID_FORM = {
    "title": "Edited title",
    "page_url": "https://a.example/page",
    "severity": "Moderate",
    "wcag_criterion": "2.4.7 Focus Visible",
    "description": "Edited description",
}


def login(client, user_id: int):
    return client.post("/login", data={"user_id": str(user_id)})


def get_issue(issue_id: int) -> Issue:
    return Issue.query.get(issue_id)
