import datetime
import jwt
import pytest
from unittest.mock import MagicMock, patch
from app import app
from tests.test_login_jwt import SECRET_KEY


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

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero,
            "ano_publicacao": self.ano_publicacao
        }


"""def test_cadastro_livro(client):
    mock_livro = LivroMock(
        id="1",
        titulo="Livro Mockado",
        autor="Autor X",
        genero="Aventura",
        ano_publicacao="2020",
    )

    with patch(
        "controllers.livros_controller.bd.cadastrarLivro",
        return_value=mock_livro
    ):
        response = client.post(
            "/livros/",
            json={
                "titulo": "Livro Mockado",
                "autor": "Autor X",
                "genero": "Aventura",
                "ano_publicacao": "2020",
            },
        )

        assert response.status_code == 201
        data = response.get_json()

        # validação dos dados retornados
        assert data["titulo"] == "Livro Mockado"
        assert data["autor"] == "Autor X"
        assert data["genero"] == "Aventura"
        assert data["ano_publicacao"] == "2020"
"""


def test_cadastro_livro(client):
    payload = {
        "id": "123",
        "role": "usuario",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Mock da conexão do banco
    with patch("controllers.livros_controller.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        # Simular INSERT RETURNING
        mock_cursor.fetchone.return_value = (
            "livro-123",  # id
            "Livro Mockado",  # titulo
            "Autor X",  # autor
            "Aventura",  # genero
            2020,  # ano_publicacao
            None,  # imagem_url
            "pendente"  # status_aprovacao
        )

        response = client.post(
            "/livros/",
            json={
                "titulo": "Livro Mockado",
                "autor": "Autor X",
                "genero": "Aventura",
                "ano_publicacao": 2020,
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.get_json()

        assert "mensagem" in data
        assert "livro" in data
        assert data["livro"]["titulo"] == "Livro Mockado"
        assert data["livro"]["autor"] == "Autor X"
        assert data["livro"]["status_aprovacao"] == "pendente"