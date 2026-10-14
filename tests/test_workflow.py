"""Status workflow: allowed map, backend rejection (400), log row, optimistic lock (409)."""
from app.models import Issue, StatusChange, db
from app.workflow import ALLOWED_TRANSITIONS, STATUSES, allowed_targets, can_transition
from tests.helpers import ALICE, ALICE_ISSUE, login


# ---- pure workflow rules


def test_open_to_closed_is_blocked():
    assert not can_transition("Open", "Closed")


def test_fixed_and_verified_can_reopen():
    assert can_transition("Fixed", "Reopened")
    assert can_transition("Verified", "Reopened")


def test_closed_is_terminal():
    assert allowed_targets("Closed") == ()


def test_every_status_has_a_rule_and_targets_are_valid():
    assert set(ALLOWED_TRANSITIONS) == set(STATUSES)
    for targets in ALLOWED_TRANSITIONS.values():
        assert set(targets) <= set(STATUSES)


# ---- HTTP behaviour


def test_invalid_transition_rejected_with_400_and_not_logged(client, app):
    login(client, ALICE)
    response = client.post(
        f"/issues/{ALICE_ISSUE}/status", data={"to_status": "Closed", "version": "1"}
    )
    assert response.status_code == 400
    assert b"Cannot change status from Open to Closed" in response.data
    assert b"Allowed from Open: In Progress" in response.data
    with app.app_context():
        assert db.session.get(Issue, ALICE_ISSUE).status == "Open"
        assert StatusChange.query.count() == 0


def test_valid_transition_updates_status_and_writes_log(client, app):
    login(client, ALICE)
    response = client.post(
        f"/issues/{ALICE_ISSUE}/status", data={"to_status": "In Progress", "version": "1"}
    )
    assert response.status_code == 302
    with app.app_context():
        issue = db.session.get(Issue, ALICE_ISSUE)
        assert issue.status == "In Progress"
        assert issue.version == 2
        rows = StatusChange.query.filter_by(issue_id=ALICE_ISSUE).all()
        assert len(rows) == 1
        assert (rows[0].changed_by, rows[0].from_status, rows[0].to_status) == (ALICE, "Open", "In Progress")

    page = client.get(f"/issues/{ALICE_ISSUE}").data.decode()
    assert "Status history" in page
    assert "Alice Test" in page
    assert "Status changed from Open to In Progress." in page


def test_stale_version_gets_409_and_changes_nothing(client, app):
    login(client, ALICE)
    client.post(f"/issues/{ALICE_ISSUE}/status", data={"to_status": "In Progress", "version": "1"})
    # Second tab still holds version 1.
    response = client.post(
        f"/issues/{ALICE_ISSUE}/status", data={"to_status": "Fixed", "version": "1"}
    )
    assert response.status_code == 409
    assert b"changed since you loaded it" in response.data
    with app.app_context():
        issue = db.session.get(Issue, ALICE_ISSUE)
        assert issue.status == "In Progress"
        assert issue.version == 2
        assert StatusChange.query.filter_by(issue_id=ALICE_ISSUE).count() == 1


def test_detail_offers_only_allowed_targets(client):
    login(client, ALICE)
    page = client.get(f"/issues/{ALICE_ISSUE}").data.decode()
    assert 'name="to_status" value="In Progress"' in page
    assert 'value="Closed"' not in page
    assert page.count('name="to_status"') == 1


def test_closed_issue_has_no_status_form(client, app):
    with app.app_context():
        issue = db.session.get(Issue, ALICE_ISSUE)
        issue.status = "Closed"
        db.session.commit()
    login(client, ALICE)
    page = client.get(f"/issues/{ALICE_ISSUE}").data.decode()
    assert 'name="to_status"' not in page
    assert "Closed is final" in page
