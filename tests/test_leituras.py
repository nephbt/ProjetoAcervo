import pytest
from unittest.mock import MagicMock, patch
from functools import wraps
import jwt
import datetime

from controllers.auth_utils import SECRET_KEY

from controllers.auth_utils import SECRET_KEY

# ----------------------------------------
# MOCK DECORATORS
# ----------------------------------------

def fake_verificar_usuario(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs["usuario"] = {
            "id": "123",
            "nome": "João",
            "email": "j@j.com",
            "senha": "123",
            "data_nasc": "2000-01-01",
            "role": "usuario"
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
    '''with patch("controllers.leituras_controller.verificar_usuario", fake_verificar_usuario), \
         patch("controllers.leituras_controller.verificar_livro", fake_verificar_livro):

        from app import app
        app.testing = True
        client = app.test_client()

    return client'''
    with patch("controllers.auth_utils.verificar_usuario", fake_verificar_usuario), \
            patch("controllers.auth_utils.verificar_livro", fake_verificar_livro):
        from app import app
        app.testing = True
        client = app.test_client()

    return client


# ----------------------------------------
# TESTE REFEITO – FUNCIONA
# ----------------------------------------
def test_registrar_leitura_sucesso(client):
    # Criar token JWT válido com o MESMO ID da URL
    payload = {
        "id": "123",  # Mesmo ID que será usado na URL
        "role": "usuario",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Mock do livro que será buscado
    livro_mock = {
        "id": "456",
        "titulo": "Livro A",
        "autor": "Autor X",
        "genero": "Ficção",
        "ano_publicacao": 2020,
        "imagem_url": None,
        "status_aprovacao": "aprovado"  # IMPORTANTE: precisa estar aprovado
    }

    # Mock da lista encadeada
    with patch("controllers.leituras_controller.gerenciador_leituras.obter_lista") as mock_obter_lista, \
            patch("controllers.leituras_controller.buscar_livro_por_id", return_value=livro_mock), \
            patch("controllers.leituras_controller.limpar_cache_usuario"), \
            patch("controllers.leituras_controller.get_connection") as mock_conn:
        # Mock da lista encadeada
        mock_lista = MagicMock()
        mock_lista.contem.return_value = False  # Livro ainda não foi lido
        mock_lista.tamanho.return_value = 1
        mock_obter_lista.return_value = mock_lista

        # Mock do cursor do banco
        mock_cursor = MagicMock()
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        # Simular INSERT RETURNING
        mock_cursor.fetchone.return_value = (
            "leitura-123",  # id
            "Lido",  # status
            5,  # avaliacao
            datetime.datetime.now(),  # data_leitura
            "Excelente"  # comentario
        )

        response = client.post(
            "/leituras/123/456",  # usuario_id=123, livro_id=456
            json={
                "status": "Lido",
                "avaliacao": 5,
                "comentario": "Excelente",
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.get_json()
        assert "mensagem" in data
        assert "leitura" in data
        assert data["leitura"]["status"] == "Lido"
        assert data["leitura"]["avaliacao"] == 5
        assert data["leitura"]["id_usuario"] == "123"
        assert data["leitura"]["id_livro"] == "456"