import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    return app.test_client()


def test_cadastro_livro(client):
    with patch("controllers.livrosController.bd.cadastrarLivro") as mock_cadastrar:
        mock_cadastrar.return_value = type("Livro", (), {
            "__dict__": {
                "id": "1",
                "titulo": "Livro Mockado",
                "autor": "Autor X",
                "genero": "Aventura",
                "ano_publicacao": "2020"
            }
        })()

        response = client.post("/livros/", json={
            "titulo": "Livro Mockado",
            "autor": "Autor X",
            "genero": "Aventura",
            "ano_publicacao": "2020"
        })

        assert response.status_code == 201
        assert "Livro Mockado" in response.get_data(as_text=True)


def test_listar_todos_livros(client):
    mock_livros = [
        type("Livro", (), {"__dict__": {"titulo": "A", "autor": "B"}})(),
        type("Livro", (), {"__dict__": {"titulo": "C", "autor": "D"}})()
    ]

    with patch("controllers.livrosController.bd.livros", {1: mock_livros[0], 2: mock_livros[1]}):
        response = client.get("/livros/")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
