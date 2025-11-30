import pytest
from unittest.mock import patch


# ----------------------------------------
# MOCK DECORATORS
# ----------------------------------------
from functools import wraps

def fake_verificar_usuario(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs["usuario"] = {
            "id": "123",
            "nome": "João",
            "email": "j@j.com",
            "senha": "123",
            "data_nasc": "2000-01-01",
        }
        return f(*args, **kwargs)
    return wrapper


def fake_verificar_livro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        class LivroFake:
            id = "456"
            titulo = "Livro A"
        kwargs["livro"] = LivroFake()
        return f(*args, **kwargs)
    return wrapper

# ----------------------------------------
# FIXTURE DO CLIENT CORRETA
# ----------------------------------------
@pytest.fixture
def client():
    # Patch ANTES de importar o app
    with patch("controllers.leituras_controller.verificar_usuario", fake_verificar_usuario), \
         patch("controllers.leituras_controller.verificar_livro", fake_verificar_livro):

        # AGORA importa o app
        from app import app
        app.testing = True
        client = app.test_client()

    return client


# ----------------------------------------
# TESTE REFEITO – FUNCIONA
# ----------------------------------------
def test_registrar_leitura_sucesso(client):

    mock_leitura = type(
        "Leitura",
        (),
        {
            "id_usuario": "123",
            "id_livro": "456",
            "status": "Lido",
            "avaliacao": 5,
            "data_leitura": "2025-11-10",
            "comentario": "Excelente",
            "to_dict": lambda self: {
                "id_usuario": self.id_usuario,
                "id_livro": self.id_livro,
                "status": self.status,
                "avaliacao": self.avaliacao,
                "data_leitura": self.data_leitura,
                "comentario": self.comentario,
            },
        },
    )()

    # Patch no método do BD
    with patch("controllers.leituras_controller.bd.cadastrarLeitura", return_value=mock_leitura):

        response = client.post(
            "/leituras/123/456",
            json={
                "status": "Lido",
                "avaliacao": 5,
                "comentario": "Excelente",
                "data_leitura": "2025-11-10",
            },
        )

        assert response.status_code == 201

        data = response.get_json()
        assert data["status"] == "Lido"
        assert data["id_usuario"] == "123"
        assert data["id_livro"] == "456"
