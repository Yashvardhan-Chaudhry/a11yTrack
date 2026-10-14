"""Backend validation: validate_issue() unit rules and the create/edit HTTP contracts."""
from app.models import Issue, db
from app.validation import TITLE_MAX, validate_issue
from tests.helpers import ALICE, ALICE_ISSUE, VALID_FORM, login


# ---- validate_issue()


def test_empty_form_reports_the_three_required_fields():
    assert set(validate_issue({})) == {"title", "page_url", "severity"}


def test_valid_form_has_no_errors():
    assert validate_issue(VALID_FORM) == {}


def test_url_must_be_http_or_https():
    assert "page_url" in validate_issue({**VALID_FORM, "page_url": "ftp://a.example/"})
    assert "page_url" in validate_issue({**VALID_FORM, "page_url": "example.com"})
    assert "page_url" not in validate_issue({**VALID_FORM, "page_url": "http://x"})


def test_title_length_limit():
    assert "title" in validate_issue({**VALID_FORM, "title": "x" * (TITLE_MAX + 1)})
    assert "title" not in validate_issue({**VALID_FORM, "title": "x" * TITLE_MAX})


def test_severity_must_be_from_the_list():
    assert "severity" in validate_issue({**VALID_FORM, "severity": "Blocker"})


def test_whitespace_only_title_is_missing():
    assert "title" in validate_issue({**VALID_FORM, "title": "   "})


# ---- HTTP: create


def test_create_with_empty_form_returns_400_with_error_summary(client):
    login(client, ALICE)
    response = client.post("/issues/new", data={})
    assert response.status_code == 400
    page = response.data.decode()
    assert 'id="error-summary"' in page
    assert "<title>Error: New issue" in page
    assert 'href="#title"' in page and 'href="#page_url"' in page and 'href="#severity"' in page
    assert page.count('aria-invalid="true"') == 3


def test_create_valid_issue_redirects_to_detail(client, app):
    login(client, ALICE)
    response = client.post("/issues/new", data=VALID_FORM)
    assert response.status_code == 302
    assert "/issues/" in response.headers["Location"]
    with app.app_context():
        assert Issue.query.filter_by(title="Edited title", owner_id=ALICE).count() == 1


# ---- HTTP: edit


def test_edit_with_blank_title_returns_400(client, app):
    login(client, ALICE)
    response = client.post(
        f"/issues/{ALICE_ISSUE}/edit", data={**VALID_FORM, "title": "", "version": "1"}
    )
    assert response.status_code == 400
    with app.app_context():
        assert db.session.get(Issue, ALICE_ISSUE).title == "Alice issue"


def test_valid_edit_updates_fields_and_bumps_version(client, app):
    login(client, ALICE)
    response = client.post(f"/issues/{ALICE_ISSUE}/edit", data={**VALID_FORM, "version": "1"})
    assert response.status_code == 302
    with app.app_context():
        issue = db.session.get(Issue, ALICE_ISSUE)
        assert issue.title == "Edited title"
        assert issue.severity == "Moderate"
        assert issue.wcag_criterion == "2.4.7 Focus Visible"
        assert issue.version == 2
        assert issue.status == "Open"  # edit never touches status


def test_stale_edit_returns_409_and_keeps_values(client, app):
    login(client, ALICE)
    client.post(f"/issues/{ALICE_ISSUE}/edit", data={**VALID_FORM, "version": "1"})
    response = client.post(
        f"/issues/{ALICE_ISSUE}/edit", data={**VALID_FORM, "title": "Second tab", "version": "1"}
    )
    assert response.status_code == 409
    page = response.data.decode()
    assert "changed since you loaded it" in page
    assert 'value="Second tab"' in page
    with app.app_context():
        assert db.session.get(Issue, ALICE_ISSUE).title == "Edited title"
