from types import SimpleNamespace
import pytest
from unittest.mock import patch
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

    # Criamos um mock de usuário igual ao que o controller espera
    usuario_falso = SimpleNamespace(
        id="123",
        nome="João Teste",
        email="joao@teste.com",
        senha="12345678",
        data_nasc="2000-01-01",
        verificar_senha=lambda senha: senha == "12345678",
        to_dict=lambda: {
            "id": "123",
            "nome": "João Teste",
            "email": "joao@teste.com",
            "data_nasc": "2000-01-01"
        }
    )

    # Mockando a busca por email no banco
    with patch(
        "controllers.usuarios_controller.bd.buscarEmail",
        return_value=usuario_falso
    ):
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

    # Criar um token válido
    payload = {
        "id": "123",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    headers = {"Authorization": f"Bearer {token}"}

    # Mockamos o decorador verificar_usuario,
    # pois a rota perfil só usa requerir_token (não usa banco)
    response = client.get("/usuarios/perfil", headers=headers)

    # Se o token for válido, retorno deve ser 200
    assert response.status_code == 200

    data = response.get_json()
    assert "Bem-vindo usuário 123!" in data["mensagem"]
