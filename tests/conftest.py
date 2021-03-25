from cvp.app import app
import pytest


@pytest.fixture
def app():
    yield app


@pytest.fixture
def client(app):
    return app.test_client()

