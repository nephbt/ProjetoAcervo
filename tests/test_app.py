import uuid
from app import app

def test_homepage():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200

def test_cadastro_livros():
    livros = app.test_client()
    response = livros.post("/livros/", json={
        "titulo": "livroTeste",
        "autor": "AutorTeste",
        "genero": "GeneroTeste",
        "ano_publicacao": "AnoPublicacaoTeste",
        "imagem_url": "URLTeste"
    })
    assert response.status_code == 201

def test_cadastro_usuario():
    client = app.test_client()
    unique_email = f"teste_{uuid.uuid4().hex[:6]}@exemplo.com"
    response = client.post("/usuarios/cadastro", json={
        "nome": "Teste",
        "email": unique_email,
        "senha": "12345678",
        "data_nasc": "2000-01-01"
    })
    assert response.status_code == 201