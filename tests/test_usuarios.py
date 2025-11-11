from datetime import datetime, timedelta, timezone
import jwt
import pytest
from unittest.mock import patch
from app import app
from tests.test_login_jwt import SECRET_KEY
from controllers.auth_utils import key as SECRET_KEY


@pytest.fixture
def client():
    return app.test_client()


def test_cadastro_usuario_sucesso(client):
    with patch("controllers.usuarios_controller.bd.cadastrarUsuario") as mock_cadastrar:
        mock_cadastrar.return_value = type("Usuario", (), {
        "to_dict": lambda self: {
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
    with patch("controllers.usuarios_controller.bd.cadastrarUsuario", return_value=None):
        response = client.post("/usuarios/cadastro", json={
            "nome": "Duplicado",
            "email": "teste@teste.com",
            "senha": "123456",
            "data_nasc": "2000-01-01"
        })
        assert response.status_code == 400
        # Corrigido: acessar o valor do dicionário
        assert response.get_json()["erro"] == "E-mail já cadastrado!"



def test_login_usuario_sucesso(client):
    mock_usuario = type("Usuario", (), {
        "id": "123",
        "nome": "Teste",
        "email": "teste@teste.com",
        "verificar_senha": lambda self, senha: senha == "123456"
    })()

    with patch("controllers.usuarios_controller.bd.buscarEmail", return_value=mock_usuario):
        response = client.post("/usuarios/login", json={
            "email": "teste@teste.com",
            "senha": "123456"
        })
        assert response.status_code == 200
        assert "token" in response.get_json()

# Teste de rota protegida com token JWT
def test_rota_perfil_autenticada(client):
    # payload com datetime UTC
    payload = {"id": "123", "exp": datetime.now(timezone.utc) + timedelta(hours=2)}

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/usuarios/perfil", headers=headers)

    print("Status:", response.status_code)
    print("JSON retornado:", response.get_json())

    # asserts
    assert response.status_code == 200
    data = response.get_json()
    assert "mensagem" in data
    assert data["mensagem"] == "Bem-vindo usuário 123!"