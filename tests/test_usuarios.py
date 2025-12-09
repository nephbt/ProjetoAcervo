from datetime import datetime, timedelta, timezone
import jwt
import pytest
from unittest.mock import MagicMock, patch
from app import app
from controllers.auth_utils import SECRET_KEY


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
                "role": "usuario"
            }

    with patch("controllers.usuarios_controller.bd.cadastrarUsuario", return_value=UsuarioFake()):
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
        role = "usuario"

        def verificar_senha(self, senha):
            return senha == "123456"

    with patch("controllers.usuarios_controller.bd.buscarEmail", return_value=UsuarioFake()):
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
        "role": "usuario",
        "exp": datetime.now(timezone.utc) + timedelta(hours=2),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Mock da conexão com o banco (usado pela rota /perfil)
    with patch("controllers.usuarios_controller.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        # Simular SELECT do usuário
        mock_cursor.fetchone.return_value = (
            "123",  # id
            "Teste",  # nome
            "teste@teste.com",  # email
            "2000-01-01",  # data_nasc
            "usuario"  # role
        )

        response = client.get(
            "/usuarios/perfil",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == "123"
        assert data["nome"] == "Teste"
        assert data["email"] == "teste@teste.com"