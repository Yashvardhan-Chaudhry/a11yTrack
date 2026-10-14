"""a11yTrack application factory."""
from flask import Flask, render_template


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev-only-change-me",
        SQLALCHEMY_DATABASE_URI="sqlite:///a11ytrack.sqlite3",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    # Temporary placeholder until routes.py is implemented.
    @app.get("/")
    def hello():
        return render_template("hello.html")

    return app
