"""HTTP routes.

Ownership: every per-issue route goes through get_owned_issue_or_404(), which
filters by id AND owner_id. Not found and not owned both give 404 so the
existence of other users' issues is never leaked.

Concurrency: writes are conditional UPDATEs on `version` (optimistic lock).
Zero rows affected means someone else saved first -> HTTP 409.
"""
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import update

from .models import Issue, StatusChange, User, db, utcnow
from .validation import SEVERITIES, WCAG_CRITERIA, validate_issue
from .workflow import STATUSES, allowed_targets, can_transition

bp = Blueprint("main", __name__)

FORM_FIELDS = ("title", "description", "page_url", "wcag_criterion", "severity")

CONFLICT_MESSAGE = (
    "This issue was changed since you loaded it. "
    "Reload the page to see the latest version, then make your change again."
)


def get_current_user() -> User | None:
    if "current_user" not in g:
        user_id = session.get("user_id")
        g.current_user = db.session.get(User, user_id) if user_id else None
    return g.current_user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if get_current_user() is None:
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapped


def get_owned_issue_or_404(issue_id: int) -> Issue:
    """The single ownership gate. 404 for missing AND for not-owned."""
    user = get_current_user()
    return Issue.query.filter_by(id=issue_id, owner_id=user.id).first_or_404()


def _form_values() -> dict[str, str]:
    return {key: (request.form.get(key) or "").strip() for key in FORM_FIELDS}


# ---------------------------------------------------------------- auth


@bp.get("/")
def index():
    return redirect(url_for("main.issues_list"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    users = User.query.order_by(User.display_name).all()
    if request.method == "POST":
        user_id = request.form.get("user_id", type=int)
        user = db.session.get(User, user_id) if user_id else None
        if user is None:
            error = "Choose a user to sign in as."
            return render_template("login.html", users=users, error=error), 400
        session.clear()
        session["user_id"] = user.id
        flash(f"Signed in as {user.display_name}.")
        return redirect(url_for("main.issues_list"))
    return render_template("login.html", users=users, error=None)


@bp.post("/logout")
def logout():
    session.clear()
    flash("Signed out.")
    return redirect(url_for("main.login"))


# ---------------------------------------------------------------- list / create


@bp.get("/issues")
@login_required
def issues_list():
    user = get_current_user()
    status = request.args.get("status", "")
    severity = request.args.get("severity", "")
    query = Issue.query.filter_by(owner_id=user.id)
    if status in STATUSES:
        query = query.filter_by(status=status)
    else:
        status = ""
    if severity in SEVERITIES:
        query = query.filter_by(severity=severity)
    else:
        severity = ""
    issues = query.order_by(Issue.created_at.desc(), Issue.id.desc()).all()
    return render_template(
        "issues_list.html",
        issues=issues,
        statuses=STATUSES,
        severities=SEVERITIES,
        selected_status=status,
        selected_severity=severity,
    )


@bp.route("/issues/new", methods=["GET", "POST"])
@login_required
def issue_new():
    user = get_current_user()
    errors: dict[str, str] = {}
    values = {key: "" for key in FORM_FIELDS}
    if request.method == "POST":
        values = _form_values()
        errors = validate_issue(values)
        if not errors:
            issue = Issue(
                owner_id=user.id,
                title=values["title"],
                description=values["description"] or None,
                page_url=values["page_url"],
                wcag_criterion=values["wcag_criterion"] or None,
                severity=values["severity"],
                status="Open",
            )
            db.session.add(issue)
            db.session.commit()
            if issue.severity == "Critical":
                # Production enqueues a team-lead email here, after the commit so a
                # rolled-back issue never notifies anyone. Locally we only log it.
                current_app.logger.info(
                    "Critical issue %s created by user %s; production would enqueue "
                    "a team-lead email",
                    issue.id,
                    user.id,
                )
            flash("Issue saved.")
            return redirect(url_for("main.issue_detail", issue_id=issue.id))
    return (
        render_template(
            "issue_form.html",
            mode="new",
            issue=None,
            values=values,
            errors=errors,
            conflict=False,
            version=None,
            severities=SEVERITIES,
            wcag_criteria=WCAG_CRITERIA,
        ),
        400 if errors else 200,
    )


# ---------------------------------------------------------------- detail / edit / status


def _render_detail(issue: Issue, error: str | None = None, status_code: int = 200):
    return (
        render_template(
            "issue_detail.html",
            issue=issue,
            targets=allowed_targets(issue.status),
            error=error,
        ),
        status_code,
    )


@bp.get("/issues/<int:issue_id>")
@login_required
def issue_detail(issue_id: int):
    issue = get_owned_issue_or_404(issue_id)
    return _render_detail(issue)


@bp.route("/issues/<int:issue_id>/edit", methods=["GET", "POST"])
@login_required
def issue_edit(issue_id: int):
    issue = get_owned_issue_or_404(issue_id)
    user = get_current_user()
    errors: dict[str, str] = {}
    conflict = False

    if request.method == "GET":
        values = {key: getattr(issue, key) or "" for key in FORM_FIELDS}
        version = issue.version
    else:
        values = _form_values()
        version = request.form.get("version", type=int)
        errors = validate_issue(values)
        if not errors:
            result = db.session.execute(
                update(Issue)
                .where(Issue.id == issue.id, Issue.owner_id == user.id, Issue.version == version)
                .values(
                    title=values["title"],
                    description=values["description"] or None,
                    page_url=values["page_url"],
                    wcag_criterion=values["wcag_criterion"] or None,
                    severity=values["severity"],
                    version=Issue.version + 1,
                    updated_at=utcnow(),
                )
            )
            if result.rowcount == 1:
                db.session.commit()
                flash("Issue saved.")
                return redirect(url_for("main.issue_detail", issue_id=issue.id))
            db.session.rollback()
            conflict = True

    status_code = 409 if conflict else 400 if errors else 200
    return (
        render_template(
            "issue_form.html",
            mode="edit",
            issue=issue,
            values=values,
            errors=errors,
            conflict=conflict,
            version=version,
            severities=SEVERITIES,
            wcag_criteria=WCAG_CRITERIA,
        ),
        status_code,
    )


@bp.post("/issues/<int:issue_id>/status")
@login_required
def issue_status(issue_id: int):
    issue = get_owned_issue_or_404(issue_id)
    user = get_current_user()
    to_status = (request.form.get("to_status") or "").strip()
    version = request.form.get("version", type=int)
    from_status = issue.status

    # 1. Workflow check: the backend decides, whatever the form offered.
    if not can_transition(from_status, to_status):
        targets = allowed_targets(from_status)
        if not to_status:
            message = "Choose a new status."
        elif targets:
            message = (
                f"Cannot change status from {from_status} to {to_status}. "
                f"Allowed from {from_status}: {', '.join(targets)}."
            )
        else:
            message = f"Cannot change status from {from_status}: Closed is final."
        return _render_detail(issue, error=message, status_code=400)

    # 2. Optimistic lock: only update the row the user actually looked at.
    now = utcnow()
    result = db.session.execute(
        update(Issue)
        .where(Issue.id == issue.id, Issue.owner_id == user.id, Issue.version == version)
        .values(status=to_status, version=Issue.version + 1, updated_at=now)
    )
    if result.rowcount == 0:
        db.session.rollback()
        db.session.refresh(issue)
        return _render_detail(issue, error=CONFLICT_MESSAGE, status_code=409)

    # 3. Log the change in the same transaction as the status update.
    db.session.add(
        StatusChange(
            issue_id=issue.id,
            changed_by=user.id,
            from_status=from_status,
            to_status=to_status,
            changed_at=now,
        )
    )
    db.session.commit()
    flash(f"Status changed from {from_status} to {to_status}.")
    return redirect(url_for("main.issue_detail", issue_id=issue.id))
