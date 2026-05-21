import os
import pytest
from pathlib import Path

# Set VAULT_PATH before app.py (and config.py) are imported.
# conftest.py is loaded by pytest before any test file, so this
# assignment runs first.
FIXTURE_VAULT = str(Path(__file__).parent / "fixtures" / "vault")
os.environ["VAULT_PATH"] = FIXTURE_VAULT


@pytest.fixture(scope="session")
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
