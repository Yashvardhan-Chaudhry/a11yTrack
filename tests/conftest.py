"""Shared fixtures: an in-memory SQLite app with two users and one Open issue each."""
import pytest

from app import create_app
from app.models import Issue, User, db


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",  # in-memory; Flask-SQLAlchemy uses StaticPool
            "SECRET_KEY": "test",
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        alice = User(display_name="Alice Test")
        bob = User(display_name="Bob Test")
        db.session.add_all([alice, bob])
        db.session.flush()
        db.session.add(
            Issue(owner_id=alice.id, title="Alice issue", page_url="https://a.example/",
                  severity="Minor", status="Open")
        )
        db.session.add(
            Issue(owner_id=bob.id, title="Bob issue", page_url="https://b.example/",
                  severity="Serious", status="Open")
        )
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
