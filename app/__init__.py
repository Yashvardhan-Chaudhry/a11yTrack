"""a11yTrack application factory."""
import os

from flask import Flask, render_template

from .models import db


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, "a11ytrack.sqlite3").replace("\\", "/")
    app.config.from_mapping(
        SECRET_KEY="dev-only-change-me",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from .routes import bp, get_current_user

    app.register_blueprint(bp)

    @app.context_processor
    def inject_current_user():
        return {"current_user": get_current_user()}

    @app.errorhandler(404)
    def not_found(_error):
        return (
            render_template(
                "error.html",
                heading="Page not found",
                message="There is no issue at this address, or it belongs to another user.",
            ),
            404,
        )

    with app.app_context():
        db.create_all()

    return app
