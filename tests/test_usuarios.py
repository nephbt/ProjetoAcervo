import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    return app.test_client()


def test_cadastro_usuario_sucesso(client):
    with patch("controllers.usuariosController.bd.cadastrarUsuario") as mock_cadastrar:
        mock_cadastrar.return_value = type("Usuario", (), {
            "to_dict": lambda self=None: {
                "id": "123",
                "nome": "Teste",
                "email": "teste@teste.com",
                "data_nasc": "2000-01-01"
            }
        })()

        response = client.post("/usuarios/cadastro", json={
            "nome": "Teste",
            "email": "teste@teste.com",
            "senha": "123456",
            "data_nasc": "2000-01-01"
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data["email"] == "teste@teste.com"


def test_cadastro_usuario_email_existente(client):
    with patch("controllers.usuariosController.bd.cadastrarUsuario", return_value=None):
        response = client.post("/usuarios/cadastro", json={
            "nome": "Duplicado",
            "email": "teste@teste.com",
            "senha": "123456",
            "data_nasc": "2000-01-01"
        })
        assert response.status_code == 400
        assert "E-mail já cadastrado" in response.get_data(as_text=True)


def test_login_usuario_sucesso(client):
    mock_usuario = type("Usuario", (), {
        "id": "123",
        "nome": "Teste",
        "email": "teste@teste.com",
        "verificar_senha": lambda self, senha: senha == "123456"
    })()

    with patch("controllers.usuariosController.bd.buscarEmail", return_value=mock_usuario):
        response = client.post("/usuarios/login", json={
            "email": "teste@teste.com",
            "senha": "123456"
        })
        assert response.status_code == 200
        assert "token" in response.get_json()
