"""Reset the local database and load demo data.

    python seed.py

Destructive: drops and recreates every table in instance/a11ytrack.sqlite3,
then inserts two demo users with four issues each. Seeded issues that are not
"Open" also get the status_changes rows that would have produced their status,
so the status log stays coherent. Names are fictional; no real personal data.
"""
from datetime import timedelta

from app import create_app
from app.models import Issue, StatusChange, User, db, utcnow

# Path each non-Open seeded status took through the workflow.
PATHS = {
    "Open": [],
    "In Progress": ["In Progress"],
    "Fixed": ["In Progress", "Fixed"],
    "Verified": ["In Progress", "Fixed", "Verified"],
}

# (title, page_url, wcag_criterion, severity, status, description)
ISSUES = {
    "Asha Rao": [
        ("Hero image has no alt text", "https://example.com/", "1.1.1 Non-text Content", "Serious", "Open",
         "The banner image conveys the campaign name but has an empty alt attribute."),
        ("Search field has no visible label", "https://example.com/search", "3.3.2 Labels or Instructions", "Moderate", "In Progress",
         "Placeholder text is the only label and disappears on input."),
        ("Focus outline removed on nav links", "https://example.com/about", "2.4.7 Focus Visible", "Critical", "Fixed",
         "outline: none is applied globally; keyboard users cannot see where they are."),
        ("Body text contrast is 3.2:1", "https://example.com/pricing", "1.4.3 Contrast (Minimum)", "Minor", "Verified",
         "Grey #8a8a8a on white fails 4.5:1 for normal text."),
    ],
    "Ben Okafor": [
        ("Modal traps keyboard focus permanently", "https://example.org/signup", "2.1.2 No Keyboard Trap", "Critical", "Open",
         "Escape does nothing and Tab cycles inside the dialog with no close control reachable."),
        ("Error messages shown only in red", "https://example.org/checkout", "1.4.1 Use of Color", "Serious", "Open",
         "Invalid fields get a red border and nothing else."),
        ("Page title identical on every page", "https://example.org/", "2.4.2 Page Titled", "Moderate", "In Progress",
         "Every page is titled Home; screen reader users cannot tell pages apart."),
        ("Data table missing header cells", "https://example.org/reports", "1.3.1 Info and Relationships", "Minor", "Fixed",
         "Headers are td elements styled bold, so cells are not associated with their headers."),
    ],
}


def seed() -> None:
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        base = utcnow() - timedelta(days=7)
        total = 0
        for name, issues in ISSUES.items():
            user = User(display_name=name)
            db.session.add(user)
            db.session.flush()
            for n, (title, url, criterion, severity, status, description) in enumerate(issues):
                created = base + timedelta(days=n, hours=n)
                issue = Issue(
                    owner_id=user.id, title=title, page_url=url, wcag_criterion=criterion,
                    severity=severity, status=status, description=description,
                    created_at=created, updated_at=created,
                )
                db.session.add(issue)
                db.session.flush()
                previous = "Open"
                for step, to_status in enumerate(PATHS[status], start=1):
                    at = created + timedelta(hours=6 * step)
                    db.session.add(StatusChange(
                        issue_id=issue.id, changed_by=user.id,
                        from_status=previous, to_status=to_status, changed_at=at,
                    ))
                    issue.updated_at = at
                    issue.version += 1
                    previous = to_status
                total += 1
        db.session.commit()
        print(f"Seeded {len(ISSUES)} users and {total} issues into {app.config['SQLALCHEMY_DATABASE_URI']}")


if __name__ == "__main__":
    seed()
