import pytest
from unittest.mock import patch
from app import app
from database import bd



@pytest.fixture
def client():
    return app.test_client()

def test_registrar_leitura_sucesso(client):
    mock_usuario = type("Usuario", (), {"id": "123", "nome": "João"})()
    mock_livro = type("Livro", (), {"id": "456", "titulo": "Livro A"})()

    mock_leitura = type("Leitura", (), {
        "id_usuario": "123",
        "id_livro": "456",
        "status": "Lido",
        "avaliacao": 5,
        "dataLeitura": "2025-11-10",
        "comentario": "Excelente"
    })()

    with patch("controllers.auth_utils.bd.usuarios", {"123": mock_usuario}), \
            patch("controllers.auth_utils.bd.livros", {"456": mock_livro}), \
            patch("controllers.leituras_controller.bd.cadastrarLeitura", return_value=mock_leitura):

        response = client.post("/leituras/123/456", json={
        "status": "Lido",
            "avaliacao": 5,
            "comentario": "Excelente",
            "data_leitura": "2025-11-10"
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "Lido"
        assert data["id_usuario"] == "123"
        assert data["id_livro"] == "456"
