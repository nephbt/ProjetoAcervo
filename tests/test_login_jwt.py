from types import SimpleNamespace
import pytest
from unittest.mock import MagicMock, patch
from app import app
import jwt
import datetime

SECRET_KEY = "chave_bem_secreta"


@pytest.fixture
def client():
    return app.test_client()


# ================================
#  TESTE LOGIN
# ================================
def test_login_usuario_mockado(client):
    usuario_falso = SimpleNamespace(
        id="123",
        nome="João Teste",
        email="joao@teste.com",
        senha="12345678",
        data_nasc="2000-01-01",
        role="usuario",
        verificar_senha=lambda senha: senha == "12345678",
        to_dict=lambda: {
            "id": "123",
            "nome": "João Teste",
            "email": "joao@teste.com",
            "data_nasc": "2000-01-01",
            "role": "usuario"
        }
    )

    with patch("controllers.usuarios_controller.bd.buscarEmail", return_value=usuario_falso):
        response = client.post(
            "/usuarios/login",
            json={"email": "joao@teste.com", "senha": "12345678"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "token" in data
        assert data["usuario"]["email"] == "joao@teste.com"

# ================================
#  TESTE ROTA PROTEGIDA
# ================================
def test_rota_protegida_com_token(client):
    payload = {
        "id": "123",
        "role": "usuario",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    headers = {"Authorization": f"Bearer {token}"}

    # Mock da conexão (rota /perfil busca no banco)
    with patch("controllers.usuarios_controller.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        # Simular SELECT
        mock_cursor.fetchone.return_value = (
            "123", "João", "joao@teste.com", "2000-01-01", "usuario"
        )

        response = client.get("/usuarios/perfil", headers=headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == "123"
        assert data["nome"] == "João"