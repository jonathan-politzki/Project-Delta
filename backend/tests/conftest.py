# conftest.py

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the directory containing main.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

@pytest.fixture
def client():
    return TestClient(app)