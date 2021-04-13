from app import app
import pytest


@pytest.fixture
def test_client():
    with app.test_client() as testing_client:
        with app.app_context():
            print(app.url_map)
            yield testing_client
