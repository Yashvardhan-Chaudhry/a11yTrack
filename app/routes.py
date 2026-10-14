"""HTTP routes. Every issue query is scoped by owner_id (see claude.md)."""
from functools import wraps

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .models import Issue, User, db
from .validation import SEVERITIES, WCAG_CRITERIA, validate_issue
from .workflow import STATUSES

bp = Blueprint("main", __name__)


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


@bp.get("/")
def index():
    return redirect(url_for("main.issues_list"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    users = User.query.order_by(User.display_name).all()
    if request.method == "POST":
        user = db.session.get(User, request.form.get("user_id", type=int))
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
    values = {"title": "", "description": "", "page_url": "", "wcag_criterion": "", "severity": ""}
    if request.method == "POST":
        values = {key: (request.form.get(key) or "").strip() for key in values}
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
            flash("Issue saved.")
            return redirect(url_for("main.issues_list"))
    status_code = 400 if errors else 200
    return (
        render_template(
            "issue_form.html",
            values=values,
            errors=errors,
            severities=SEVERITIES,
            wcag_criteria=WCAG_CRITERIA,
        ),
        status_code,
    )
