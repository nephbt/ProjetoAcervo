import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    return app.test_client()


def test_registrar_leitura_sucesso(client):
    mock_usuario = {"id": "123", "nome": "João"}
    mock_livro = {"id": "456", "titulo": "Livro A"}

    mock_leitura = type("Leitura", (), {
        "__dict__": {
            "id_usuario": "123",
            "id_livro": "456",
            "status": "Lido",
            "avaliacao": 5,
            "comentario": "Excelente"
        }
    })()

    with patch("controllers.leiturasController.bd.usuarios", {"123": mock_usuario}), \
         patch("controllers.leiturasController.bd.livros", {"456": mock_livro}), \
         patch("controllers.leiturasController.bd.cadastrarLeitura", return_value=mock_leitura):

        response = client.post("/leituras/123/456", json={
            "status": "Lido",
            "avaliacao": 5,
            "comentario": "Excelente"
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "Lido"
