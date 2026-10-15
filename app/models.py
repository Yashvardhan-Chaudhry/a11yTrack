"""Database models. Schema is locked in claude.md."""
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow() -> datetime:
    """Naive UTC timestamp (SQLite has no timezone type)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(80), nullable=False)


class Issue(db.Model):
    __tablename__ = "issues"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    page_url = db.Column(db.String(2000), nullable=False)
    wcag_criterion = db.Column(db.String(120), nullable=True)
    severity = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Open")
    version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    owner = db.relationship("User")
    status_changes = db.relationship(
        "StatusChange", back_populates="issue", order_by="StatusChange.changed_at"
    )

    # Matches the list query: WHERE owner_id = ? ORDER BY created_at DESC.
    __table_args__ = (db.Index("ix_issues_owner_created", "owner_id", "created_at"),)


class StatusChange(db.Model):
    __tablename__ = "status_changes"

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    from_status = db.Column(db.String(20), nullable=False)
    to_status = db.Column(db.String(20), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    issue = db.relationship("Issue", back_populates="status_changes")
    actor = db.relationship("User")

    # Matches the detail page: WHERE issue_id = ? ORDER BY changed_at.
    __table_args__ = (db.Index("ix_status_changes_issue_changed", "issue_id", "changed_at"),)
