"""Ownership: a user can never see, edit or change another user's issue, even by URL."""
import pytest

from app.models import Issue, db
from tests.helpers import ALICE, ALICE_ISSUE, BOB_ISSUE, VALID_FORM, login


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", f"/issues/{BOB_ISSUE}"),
        ("get", f"/issues/{BOB_ISSUE}/edit"),
        ("post", f"/issues/{BOB_ISSUE}/edit"),
        ("post", f"/issues/{BOB_ISSUE}/status"),
    ],
)
def test_other_users_issue_is_404(client, method, path):
    login(client, ALICE)
    data = {**VALID_FORM, "version": "1", "to_status": "In Progress"}
    response = getattr(client, method)(path, data=data)
    assert response.status_code == 404
    assert b"Page not found" in response.data


def test_cross_user_post_does_not_modify_anything(client, app):
    login(client, ALICE)
    client.post(f"/issues/{BOB_ISSUE}/edit", data={**VALID_FORM, "version": "1"})
    client.post(f"/issues/{BOB_ISSUE}/status", data={"to_status": "In Progress", "version": "1"})
    with app.app_context():
        bob_issue = db.session.get(Issue, BOB_ISSUE)
        assert bob_issue.title == "Bob issue"
        assert bob_issue.status == "Open"
        assert bob_issue.version == 1


def test_list_shows_only_own_issues(client):
    login(client, ALICE)
    page = client.get("/issues").data.decode()
    assert "Alice issue" in page
    assert "Bob issue" not in page


def test_missing_issue_is_also_404(client):
    login(client, ALICE)
    assert client.get("/issues/999").status_code == 404


def test_unauthenticated_requests_redirect_to_login(client):
    for path in ("/issues", f"/issues/{ALICE_ISSUE}", f"/issues/{ALICE_ISSUE}/edit", "/issues/new"):
        response = client.get(path)
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/login")
