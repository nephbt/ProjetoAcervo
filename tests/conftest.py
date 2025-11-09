#conftest.py pode centralizar o test_client do Flask, assim não precisa repetir em todo teste.
import pytest
from app import app

@pytest.fixture
def client():
    return app.test_client()
