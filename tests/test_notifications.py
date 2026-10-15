"""Critical-issue notification hook: locally a log line, in production a queued email."""
import logging

from tests.helpers import ALICE, VALID_FORM, login


def _create(client, severity):
    return client.post("/issues/new", data={**VALID_FORM, "severity": severity})


def test_critical_issue_logs_notification_line(client, caplog):
    login(client, ALICE)
    with caplog.at_level(logging.INFO):
        response = _create(client, "Critical")
    assert response.status_code == 302
    assert any("Critical issue" in r.getMessage() for r in caplog.records)


def test_non_critical_issue_does_not_log(client, caplog):
    login(client, ALICE)
    with caplog.at_level(logging.INFO):
        response = _create(client, "Minor")
    assert response.status_code == 302
    assert not any("Critical issue" in r.getMessage() for r in caplog.records)
