from datetime import datetime, timedelta, timezone
import jwt
import pytest
from unittest.mock import patch
from app import app
from controllers.auth_utils import key as SECRET_KEY


@pytest.fixture
def client():
    return app.test_client()


# ----------------------------------------------------
# TESTE 1 — Cadastro de usuário com sucesso
# ----------------------------------------------------
def test_cadastro_usuario_sucesso(client):
    class UsuarioFake:
        def to_dict(self):
            return {
                "id": "123",
                "nome": "Teste",
                "email": "teste@teste.com",
                "data_nasc": "2000-01-01",
            }

    with patch("controllers.usuarios_controller.bd.cadastrarUsuario",
               return_value=UsuarioFake()):
        response = client.post(
            "/usuarios/cadastro",
            json={
                "nome": "Teste",
                "email": "teste@teste.com",
                "senha": "123456",
                "data_nasc": "2000-01-01",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["email"] == "teste@teste.com"


# ----------------------------------------------------
# TESTE 2 — Cadastro com e-mail duplicado
# ----------------------------------------------------
def test_cadastro_usuario_email_existente(client):
    with patch("controllers.usuarios_controller.bd.cadastrarUsuario",
               return_value=None):
        response = client.post(
            "/usuarios/cadastro",
            json={
                "nome": "Duplicado",
                "email": "teste@teste.com",
                "senha": "123456",
                "data_nasc": "2000-01-01",
            },
        )

        assert response.status_code == 400
        assert response.get_json()["erro"] == "E-mail já cadastrado!"


# ----------------------------------------------------
# TESTE 3 — Login com sucesso
# ----------------------------------------------------
def test_login_usuario_sucesso(client):
    class UsuarioFake:
        id = "123"
        nome = "Teste"
        email = "teste@teste.com"

        def verificar_senha(self, senha):
            return senha == "123456"

    with patch("controllers.usuarios_controller.bd.buscarEmail",
               return_value=UsuarioFake()):
        response = client.post(
            "/usuarios/login",
            json={"email": "teste@teste.com", "senha": "123456"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "token" in data
        assert data["usuario"]["email"] == "teste@teste.com"


# ----------------------------------------------------
# TESTE 4 — Acesso à rota protegida com token válido
# ----------------------------------------------------
def test_rota_perfil_autenticada(client):
    payload = {
        "id": "123",
        "exp": datetime.now(timezone.utc) + timedelta(hours=2),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    response = client.get(
        "/usuarios/perfil",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["mensagem"] == "Bem-vindo usuário 123!"
