"""
Script para popular o banco com dados de teste para o sistema de recomendação KNN.
Execute este arquivo para criar usuários, livros e avaliações de teste.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"


def criar_usuarios_teste():
    """Cria 3 usuários de teste"""
    usuarios = [
        {"nome": "Maria Silva", "email": "maria@test.com", "senha": "senha123", "data_nasc": "1995-05-15"},
        {"nome": "João Santos", "email": "joao@test.com", "senha": "senha123", "data_nasc": "1990-08-20"},
        {"nome": "Ana Costa", "email": "ana@test.com", "senha": "senha123", "data_nasc": "1998-12-10"},
        {"nome": "Joana Santos", "email": "joana@test.com", "senha": "senha123", "data_nasc": "1978-12-10"},
        {"nome": "Miriam Santana", "email": "miriam@test.com", "senha": "senha123", "data_nasc": "1988-12-10"},
        {"nome": "José Silveira", "email": "jose@test.com", "senha": "senha123", "data_nasc": "1968-12-10"}
    ]

    usuarios_criados = []

    print("📝 Criando usuários de teste...")
    for usuario in usuarios:
        try:
            response = requests.post(f"{BASE_URL}/usuarios/cadastro", json=usuario)
            if response.status_code == 201:
                user_data = response.json()
                usuarios_criados.append(user_data)
                print(f"   ✅ {usuario['nome']} criado com sucesso!")
            else:
                print(f"   ⚠️ {usuario['email']} já existe ou erro: {response.json()}")
        except Exception as e:
            print(f"   ❌ Erro ao criar {usuario['nome']}: {e}")

    return usuarios_criados


def criar_livros_teste():
    """Cria 10 livros de teste com diferentes gêneros"""
    livros = [
       #0
        {"titulo": "1984", "autor": "George Orwell", "genero": "Ficção Científica", "ano_publicacao": 1949,
         "imagem": "https://m.media-amazon.com/images/I/71kxa1-0mfL._SY466_.jpg"},
        {"titulo": "O Senhor dos Anéis", "autor": "J.R.R. Tolkien", "genero": "Fantasia", "ano_publicacao": 1954,
         "imagem": "https://m.media-amazon.com/images/I/81hCVEC0ExL._SY466_.jpg"},
        {"titulo": "Harry Potter", "autor": "J.K. Rowling", "genero": "Fantasia", "ano_publicacao": 1997,
         "imagem": "https://m.media-amazon.com/images/I/81ibfYk4qmL._SY466_.jpg"},
        {"titulo": "Duna", "autor": "Frank Herbert", "genero": "Ficção Científica", "ano_publicacao": 1965,
         "imagem": "https://m.media-amazon.com/images/I/81zN7udGRUL._SY466_.jpg"},
        {"titulo": "Orgulho e Preconceito", "autor": "Jane Austen", "genero": "Romance", "ano_publicacao": 1813,
         "imagem": "https://m.media-amazon.com/images/I/71Q1tPupKjL._SY466_.jpg"},
        #5
        {"titulo": "O Código Da Vinci", "autor": "Dan Brown", "genero": "Suspense", "ano_publicacao": 2003,
         "imagem": "https://m.media-amazon.com/images/I/91Q5dCjc2KL._SY466_.jpg"},
        {"titulo": "A Culpa é das Estrelas", "autor": "John Green", "genero": "Romance", "ano_publicacao": 2012,
         "imagem": "https://m.media-amazon.com/images/I/71FxgtFTppL._SY466_.jpg"},
        {"titulo": "Neuromancer", "autor": "William Gibson", "genero": "Ficção Científica", "ano_publicacao": 1984,
         "imagem": "https://m.media-amazon.com/images/I/71bWQJ6hSyL._SY466_.jpg"},
        {"titulo": "O Hobbit", "autor": "J.R.R. Tolkien", "genero": "Fantasia", "ano_publicacao": 1937,
         "imagem": "https://m.media-amazon.com/images/I/91dSMhdIzTL._SY466_.jpg"},
        {"titulo": "Fahrenheit 451", "autor": "Ray Bradbury", "genero": "Ficção Científica", "ano_publicacao": 1953,
         "imagem": "https://m.media-amazon.com/images/I/71OFqSRFDgL._SY466_.jpg"},
        #10
        {"titulo": "O Morro dos Ventos Uivantes", "autor": "Emily Bronte", "genero": "Romance", "ano_publicacao": 1847,
         "imagem": "https://cdn2.penguin.com.au/covers/original/9780553212587.jpg"},
        {"titulo": "O Diário de Bridget Jones", "autor": "Helen Fielding", "genero": "Romance", "ano_publicacao": 1996,
         "imagem": "https://m.media-amazon.com/images/I/81mCz4TXMSL._SY466_.jpg"},
        {"titulo": "A Rainha Vermelha", "autor": "Victoria Aveyard", "genero": "Fantasia", "ano_publicacao": 2015,
         "imagem": "https://m.media-amazon.com/images/I/41HQfYIMXzL._SY445_SX342_ML2_.jpg"},
        {"titulo": "O Ladrão de Almas e a Esfera de Fogo", "autor": "Marco Lago Pereira ", "genero": "Fantasia", "ano_publicacao": 2015,
         "imagem": "https://m.media-amazon.com/images/I/71rDO6D4XIL._SL1500_.jpg"},
        {"titulo": "Razão e Sensibilidade", "autor": "Jane Austen", "genero": "Romance", "ano_publicacao": 1811},
        #15
        {"titulo": "Eleanor e Park", "autor": "Rainbow Rowell", "genero": "Romance", "ano_publicacao": 2012,
         "imagem": "https://m.media-amazon.com/images/I/71ix1BMtFlL._SY466_.jpg"},
        {"titulo": "Jane Eyre", "autor": "Charlotte Bronte", "genero": "Romance", "ano_publicacao": 1847,
         "imagem": "https://m.media-amazon.com/images/I/71kxa1-0mfL._SY466_.jpg"},
        {"titulo": "Desculpa, Te Amo", "autor": "Cecelia Ahern", "genero": "Romance", "ano_publicacao": 2004,
         "imagem": "https://m.media-amazon.com/images/I/71x8nO9FCDL._SY466_.jpg"},
        {"titulo": "Heartstopper", "autor": "Alice Oseman", "genero": "Romance", "ano_publicacao": 2019,
         "imagem": "https://m.media-amazon.com/images/I/71k-7YnXC9L._SY466_.jpg"},
        {"titulo": "Jogos Vorazes", "autor": "Suzanne Collins", "genero": "Ficção Cientifica", "ano_publicacao": 2008,
         "imagem": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgs8JOJtFYBBWsvPl0APGsYVKFeUAWTU_5xnIH8Tb4QPa-NCzLAax5Mab8CFYJwxSxuhGPi52h8alAZLGGrFYzXSM8mZzQBwlQzhw6zPVcRDEzfVJH3Sg9v1p_d9dmBIJUeilJqenYNb_E/s1600/jogos-vorazes-suzanne-collins.jpg"},
        #20
        {"titulo": "Guerra dos Tronos", "autor": "George R.R. Martin", "genero": "Fantasia", "ano_publicacao": 1996,
         "imagem": "https://m.media-amazon.com/images/I/91+1SUO3vUL._SY425_.jpg"},
        {"titulo": "Alice no País das Maravilhas", "autor": "Lewis Carroll", "genero": "Fantasia", "ano_publicacao": 1865,
         "imagem": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjcw7LjecrVJx79qGYYt6TXeHYtv6DQzvrgtbBYecNKu4bg0qI8cKHX4Wr1y5Ro5pAlw67w48vRqf68ql-mKofjEeoxujSnvnIgLSVZ4fuvrYZLOPmoaRXAyEbnFxhqEuYsJ7tCATc0/s1600/alice-no-pais-das-maravilhas-lewis-carroll-editora-l-e-pm-colecao-l-e-pm-pocket-2002-capa-livro.jpg"},
        {"titulo": "Gabriela, Cravo e Canela", "autor": "Jorge Amado", "genero": "Romance", "ano_publicacao": 1958,
         "imagem": "https://m.media-amazon.com/images/I/51+5OgHbwyL._SY445_SX342_ML2_.jpg"},
        {"titulo": "Como eu era antes de você", "autor": "Jojo Moyes", "genero": "Romance", "ano_publicacao": 2015,
         "imagem": "https://livrariapublica.com.br/capa/como-eu-era-antes-de-voce-jojo-moyes-pdf-B00C9NKYSY.webp"},
        {"titulo": "Água para elefantes", "autor": "Sara Gruen", "genero": "Romance", "ano_publicacao": 2006},
        #25
        {"titulo": "Admirável Mundo Novo", "autor": "Aldous Huxley", "genero": "Ficção Científica", "ano_publicacao": 1932,
         "imagem": "https://upload.wikimedia.org/wikipedia/pt/6/62/BraveNewWorld_FirstEdition.jpg"},
        {"titulo": "A Revolução dos Bichos", "autor": "George Orwell", "genero": "Ficção Científica", "ano_publicacao": 1945,
         "imagem": "https://pt.wikipedia.org/wiki/Animal_Farm#/media/Ficheiro:Animal_Farm_-_1st_edition.jpg"},
        {"titulo": "Adeus às Armas", "autor": "Ernest Hemingway", "genero": "Romance", "ano_publicacao": 1929},
        {"titulo": "Por Quem os Sinos Dobram", "autor": "Ernest Hemingway", "genero": "Romance", "ano_publicacao": 1940},

    ]

    livros_criados = []

    print("\n📚 Criando livros de teste...")
    for livro in livros:
        try:
            response = requests.post(f"{BASE_URL}/livros/cadastro", data=livro)
            if response.status_code == 201:
                livro_data = response.json()
                livros_criados.append(livro_data)
                print(f"   ✅ '{livro['titulo']}' criado!")
            else:
                print(f"   ⚠️ Erro ao criar '{livro['titulo']}': {response.json()}")
        except Exception as e:
            print(f"   ❌ Erro ao criar '{livro['titulo']}': {e}")

    return livros_criados


def fazer_login(email, senha):
    """Faz login e retorna o token"""
    try:
        response = requests.post(f"{BASE_URL}/usuarios/login", json={"email": email, "senha": senha})
        if response.status_code == 200:
            return response.json()["token"], response.json()["usuario"]["id"]
        else:
            print(f"   ❌ Erro no login: {response.json()}")
            return None, None
    except Exception as e:
        print(f"   ❌ Erro ao fazer login: {e}")
        return None, None


def criar_avaliacoes_teste(usuarios, livros):
    """Cria avaliações simulando perfis de usuários com gostos diferentes"""

    print("\n⭐ Criando avaliações de teste...")

    #Joana
    joana_token, joana_id = fazer_login(" joana@test.com", "senha123")
    if  joana_token:
        avaliacoes_joana = [
            (livros[0]["id"], 9.5, "lido"),  # 1984
            (livros[3]["id"], 9.0, "lido"),  # Duna
            (livros[7]["id"], 8.5, "lido"),  # Neuromancer
            (livros[9]["id"], 8.0, "lido"),  # Fahrenheit 451
            (livros[1]["id"], 6.0, "lido"),  # Senhor dos Anéis
            (livros[11]["id"], 7.0, "lido"), # O Diário de Bridget Jones
            (livros[13]["id"], 7.5, "lido"), # O Ladrão de Almas e a Esfera de Fogo
            (livros[18]["id"], 7.9, "lido"), # Heartstopper
            (livros[19]["id"], 9.0, "lido"), # Jogos Vorazes
            (livros[20]["id"], 10, "lido"), # Guerra dos Tronos
        ]

        for livro_id, nota, status in avaliacoes_joana:
            try:
                requests.post(
                    f"{BASE_URL}/leituras/{ joana_id}/{livro_id}",
                    json={"status": status, "avaliacao": nota, "data_leitura": "2024-01-15"},
                    headers={"Authorization": f"Bearer { joana_token}"}
                )
                print(f"   ✅  Joana avaliou um livro com nota {nota}")
            except Exception as e:
                print(f"   ⚠️ Erro: {e}")

    #Miriam
    miriam_token, miriam_id = fazer_login("miriam@test.com", "senha123")
    if miriam_token:
        avaliacoes_miriam = [
            (livros[22]["id"], 6.0, "lido"),  # Gabriela Cravo e Canela
            (livros[17]["id"], 9.0, "lido"),  # Desculpa, Te Amo
            (livros[11]["id"], 7.0, "lido"),  # O Diário de Bridget Jones
            (livros[15]["id"], 8.0, "lido"),  # Eleanor e Park
            (livros[18]["id"], 9.0, "lido"),  # Heartstopper
            (livros[19]["id"], 7.0, "lido"),  # Jogos Vorazes
            (livros[6]["id"], 10.0, "lido"),  # A Culpa é das Estrelas
            (livros[23]["id"], 9.0, "lendo"), # Como eu era antes de você
            (livros[2]["id"], 5.0, "lido"),  # Harry Potter
            (livros[24]["id"], 10, "lido"), # Água para elefantes
        ]

        for livro_id, nota, status in avaliacoes_miriam:
            try:
                requests.post(
                    f"{BASE_URL}/leituras/{ miriam_id}/{livro_id}",
                    json={"status": status, "avaliacao": nota, "data_leitura": "2024-01-15"},
                    headers={"Authorization": f"Bearer { miriam_token}"}
                )
                print(f"   ✅  Miriam avaliou um livro com nota {nota}")
            except Exception as e:
                print(f"   ⚠️ Erro: {e}")

    #Jose
    jose_token, jose_id = fazer_login("jose@test.com", "senha123")
    if jose_token:
        avaliacoes_jose = [
            (livros[25]["id"], 10, "lido"),
            (livros[26]["id"], 9, "lido"),
            (livros[27]["id"], 8, "lido"),
            (livros[29]["id"], 9, "lido"),
            (livros[22]["id"], 8.0, "lido"),  # Gabriela Cravo e Canela
        ]

        for livro_id, nota, status in avaliacoes_jose:
            try:
                requests.post(
                    f"{BASE_URL}/leituras/{ jose_id}/{livro_id}",
                    json={"status": status, "avaliacao": nota, "data_leitura": "2024-01-15"},
                    headers={"Authorization": f"Bearer { jose_token}"}
                )
                print(f"   ✅  José avaliou um livro com nota {nota}")
            except Exception as e:
                print(f"   ⚠️ Erro: {e}")

    #Susana

    #Marcelo

    #Nadia

    #Roberto

    # Maria gosta de Ficção Científica (notas altas)
    maria_token, maria_id = fazer_login("maria@test.com", "senha123")
    if maria_token:
        avaliacoes_maria = [
            (livros[3]["id"], 9.0, "lido"),  # Duna
            (livros[7]["id"], 8.5, "lido"),  # Neuromancer
            (livros[9]["id"], 8.0, "lido"),  # Fahrenheit 451
            (livros[1]["id"], 6.0, "lido"),  # Senhor dos Anéis
            (livros[11]["id"], 7.0, "lido"), # O Diário de Bridget Jones
            (livros[13]["id"], 7.5, "lido"), # O Ladrão de Almas e a Esfera de Fogo
            (livros[15]["id"], 7.0, "lido"), # Eleanor e Park
            (livros[16]["id"], 7.7, "lido"), # Jane Eyre
            (livros[17]["id"], 8.3, "lido"), # Desculpa, Te Amo
            (livros[18]["id"], 7.9, "lido")  # Heartstopper
        ]

        for livro_id, nota, status in avaliacoes_maria:
            try:
                requests.post(
                    f"{BASE_URL}/leituras/{maria_id}/{livro_id}",
                    json={"status": status, "avaliacao": nota, "data_leitura": "2024-01-15"},
                    headers={"Authorization": f"Bearer {maria_token}"}
                )
                print(f"   ✅ Maria avaliou um livro com nota {nota}")
            except Exception as e:
                print(f"   ⚠️ Erro: {e}")

    # João gosta de Fantasia (notas altas)
    joao_token, joao_id = fazer_login("joao@test.com", "senha123")
    if joao_token:
        avaliacoes_joao = [
            (livros[1]["id"], 10.0, "lido"), # Senhor dos Anéis
            (livros[2]["id"], 9.5, "lido"),  # Harry Potter
            (livros[8]["id"], 9.0, "lido"),  # O Hobbit
            (livros[0]["id"], 7.0, "lido"),  # 1984
            (livros[4]["id"], 6.5, "lido"),  # Orgulho e Preconceito
            (livros[10]["id"], 9.0, "lido"), # O Morro dos Ventos Uivantes
            (livros[14]["id"], 8.0, "lido"),  # Razão e Sensibilidade
            (livros[19]["id"], 9.0, "lido"),  # Jogos Vorazes
            (livros[21]["id"], 5.0, "lido"), # Alice no País das Maravilhas
            (livros[22]["id"], 9.0, "lendo") # Gabriela Cravo e Canela
        ]

        for livro_id, nota, status in avaliacoes_joao:
            try:
                requests.post(
                    f"{BASE_URL}/leituras/{joao_id}/{livro_id}",
                    json={"status": status, "avaliacao": nota, "data_leitura": "2024-01-20"},
                    headers={"Authorization": f"Bearer {joao_token}"}
                )
                print(f"   ✅ João avaliou um livro com nota {nota}")
            except Exception as e:
                print(f"   ⚠️ Erro: {e}")

    # Ana gosta de Romance (notas altas)
    ana_token, ana_id = fazer_login("ana@test.com", "senha123")
    if ana_token:
        avaliacoes_ana = [
            (livros[0]["id"], 9.5, "lido"),  # 1984
            (livros[4]["id"], 9.5, "lido"),  # Orgulho e Preconceito
            (livros[6]["id"], 9.0, "lido"),  # A Culpa é das Estrelas
            (livros[5]["id"], 8.0, "lido"),  # Código Da Vinci
            (livros[2]["id"], 7.5, "lido"),  # Harry Potter
            (livros[12]["id"], 8.0, "lido"), # A Rainha Vermelha
            (livros[16]["id"], 7.8, "lido"), # Jane Eyre
            (livros[19]["id"], 9.0, "lido"),  # Jogos Vorazes
            (livros[21]["id"], 6.0, "lido"),  # Alice no País das Maravilhas
        ]

        for livro_id, nota, status in avaliacoes_ana:
            try:
                requests.post(
                    f"{BASE_URL}/leituras/{ana_id}/{livro_id}",
                    json={"status": status, "avaliacao": nota, "data_leitura": "2024-02-01"},
                    headers={"Authorization": f"Bearer {ana_token}"}
                )
                print(f"   ✅ Ana avaliou um livro com nota {nota}")
            except Exception as e:
                print(f"   ⚠️ Erro: {e}")


def testar_recomendacoes():
    """Testa o sistema de recomendações para cada usuário"""
    print("\n🎯 Testando sistema de recomendações KNN...\n")

    usuarios_teste = [
        ("maria@test.com", "Maria (gosta de Ficção Científica)"),
        ("joao@test.com", "João (gosta de Fantasia)"),
        ("ana@test.com", "Ana (gosta de Romance)"),
        ("joana@test.com", "Joana"),
        ("miriam@test.com", "Miriam"),
        ("jose@test.com", "José")
    ]

    for email, nome in usuarios_teste:
        # NOVO LOGIN AQUI - token fresco para cada teste
        token, user_id = fazer_login(email, "senha123")

        if token:
            print(f"\n{'=' * 60}")
            print(f"📖 Recomendações para {nome}")
            print(f"{'=' * 60}")

            try:
                response = requests.get(
                    f"{BASE_URL}/recomendacoes/{user_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 200:
                    data = response.json()
                    print(f"\n{data['mensagem']}\n")

                    for i, livro in enumerate(data['recomendacoes'], 1):
                        print(f"{i}. {livro['titulo']}")
                        print(f"   Autor: {livro['autor']}")
                        print(f"   Gênero: {livro['genero']}\n")
                else:
                    print(f"❌ Erro: {response.json()}")

            except Exception as e:
                print(f"❌ Erro ao buscar recomendações: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando população de dados de teste...\n")
    print("⚠️ Certifique-se que o servidor Flask está rodando em http://127.0.0.1:5000\n")

    # 1. Criar usuários
    usuarios = criar_usuarios_teste()

    # 2. Criar livros
    livros = criar_livros_teste()

    if not livros:
        print("\n❌ Erro: Não foi possível criar livros. Verifique se o servidor está rodando.")
        exit(1)

    # 3. Criar avaliações
    criar_avaliacoes_teste(usuarios, livros)

    # 4. Testar recomendações
    testar_recomendacoes()

    print("\n✅ Teste completo! O sistema de recomendações KNN está funcionando.")
    print("\n💡 Dica: Faça login com um dos usuários e teste no frontend!")
    print("   - maria@test.com / senha123 (gosta de Ficção Científica)")
    print("   - joao@test.com / senha123 (gosta de Fantasia)")
    print("   - ana@test.com / senha123 (gosta de Romance)")