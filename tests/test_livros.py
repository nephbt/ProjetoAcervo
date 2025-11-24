import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    return app.test_client()

class LivroMock:
    def __init__(self, id, titulo, autor, genero, ano_publicacao):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.ano_publicacao = ano_publicacao

def test_cadastro_livro(client):
    mock_livro = LivroMock(
        id="1",
        titulo="Livro Mockado",
        autor="Autor X",
        genero="Aventura",
        ano_publicacao="2020"
    )

    with patch("controllers.livros_controller.bd.cadastrarLivro", return_value=mock_livro):
        response = client.post("/livros/", json={
            "titulo": "Livro Mockado",
            "autor": "Autor X",
            "genero": "Aventura",
            "ano_publicacao": "2020"
        })

        print("Status:", response.status_code)
        print("JSON retornado:", response.get_json())

        assert response.status_code == 201
        data = response.get_json()
        assert data["titulo"] == "Livro Mockado"
        assert data["autor"] == "Autor X"
        assert data["genero"] == "Aventura"
        assert data["ano_publicacao"] == "2020"
