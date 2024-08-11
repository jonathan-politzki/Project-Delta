# conftest.py

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from main import app
except ImportError as e:
    print(f"Error importing app: {e}")
    app = None

@pytest.fixture
def client():
    if app is None:
        pytest.skip("App import failed")
    return TestClient(app)