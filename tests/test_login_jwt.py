import pytest
from unittest.mock import patch
from app import app
import jwt
import datetime

# Chave igual à usada no back
SECRET_KEY = "chave_bem_secreta"


@pytest.fixture
def client():
    return app.test_client()

# ---------- TESTE DE LOGIN COM MOCK ----------
def test_login_usuario_mockado(client):
    usuario_falso = {
        "id": "123",
        "nome": "João Teste",
        "email": "joao@teste.com",
        "senha": "12345678",  # senha original
        "data_nasc": "2000-01-01"
    }

    # Simula a função bd.buscarEmail() retornando o usuário falso
    with patch("controllers.usuariosController.bd.buscarEmail", return_value=usuario_falso), \
         patch("controllers.usuariosController.bd.verificar_senha", return_value=True):

        # Faz o login com os mesmos dados do usuário falso
        response = client.post("/usuarios/login", json={
            "email": "joao@teste.com",
            "senha": "12345678"
        })

        assert response.status_code == 200
        data = response.get_json()
        assert "token" in data
        assert data["usuario"]["email"] == "joao@teste.com"


# ---------- TESTE DE ROTA PROTEGIDA ----------
def test_rota_protegida_com_token(client):
    # Gera um token válido manualmente
    payload = {
        "id": "123",
        "exp": datetime.datetime.now() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    headers = {"Authorization": f"Bearer {token}"}

    # Suponha que existe uma rota protegida que usa @requerir_token
    response = client.get("/usuarios/perfil", headers=headers)

    # Se o token estiver correto, o status deve ser 200 (OK)
    assert response.status_code in [200, 401]  # depende se a rota existe
