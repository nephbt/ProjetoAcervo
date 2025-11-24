import uuid
from database import bd


def popular_banco_teste():
    """
    Popula o banco de dados com usuários, livros e leituras usando SQLite direto
    """
    print("🌱 Iniciando seed do banco de dados...")

    # Usuários
    usuarios_data = [
        ("Maria Silva", "maria@test.com", "senha123", "1995-05-15"),
        ("João Santos", "joao@test.com", "senha123", "1990-08-20"),
        ("Ana Costa", "ana@test.com", "senha123", "1998-12-10"),
        ("Joana Santos", "joana@test.com", "senha123", "1978-12-10"),
        ("Miriam Santana", "miriam@test.com", "senha123", "1988-12-10"),
        ("José Silveira", "jose@test.com", "senha123", "1968-12-10"),
        ("Karen dos Santos", "karen@test.com", "senha123", "1977-01-20"),
        ("Alan Silva", "alan@test.com", "senha123", "1989-12-13"),
        ("Bruno da Silva", "bruno@test.com", "senha123", "1999-06-10"),
        ("Juliana da Costa", "juliana@test.com", "senha123", "2000-07-21"),
        ("Arthur Duarte", "arthur@test.com", "senha123", "1995-06-09"),
        ("Amanda Soares", "amanda@test.com", "senha123", "1995-01-20"),
        ("Paulo dos Santos", "paulo@test.com", "senha123", "2005-09-29"),
        ("Ana Paula", "anapaula@test.com", "senha123", "2001-12-11"),
        ("Daniel Santana", "daniel@test.com", "senha123", "1980-05-05"),
        ("Larissa da Costa", "larissa@test.com", "senha123", "1988-09-21"),
        ("Luís Gomes", "luis@test.com", "senha123", "1993-03-24"),
        ("Silvia Santana", "silvia@test.com", "senha123", "1994-09-10"),
        ("Alexandre da Silva", "alexandre@test.com", "senha123", "1996-03-30"),
        ("César Daniel", "cesar@test.com", "senha123", "1997-04-03"),
        ("Cássia Moraes", "cassia@test.com", "senha123", "1998-05-30"),
        ("Clara Martins", "clara@test.com", "senha123", "1999-09-30"),
        ("Marisa Santana", "marissa@test.com", "senha123", "1985-09-30"),
        ("Roberto da Silva", "roberto@test.com", "senha123", "1988-09-27"),
        ("Eduardo dos Santos", "eduardo@test.com", "senha123", "2000-01-29"),
    ]

    usuario_ids = []
    for nome, email, senha, data_nasc in usuarios_data:
        uid = str(uuid.uuid4())
        usuario = bd.cadastrarUsuario(uid, nome, email, senha, data_nasc)
        if usuario:
            usuario_ids.append(uid)
            print(f"✓ Usuário criado: {email}")
        else:
            user = bd.buscarEmail(email)
            if user:
                usuario_ids.append(user.id)

    print(f"✓ {len(usuario_ids)} usuários no total\n")

    # Livros
    livros_data = [
        ("1984", "George Orwell", "Ficção Científica", 1949, "https://m.media-amazon.com/images/I/71kxa1-0mfL._SY466_.jpg"),
        ("O Senhor dos Anéis", "J.R.R. Tolkien", "Fantasia", 1954, "https://m.media-amazon.com/images/I/81hCVEC0ExL._SY466_.jpg"),
        ("Harry Potter", "J.K. Rowling", "Fantasia", 1997, "https://m.media-amazon.com/images/I/81ibfYk4qmL._SY466_.jpg"),
        ("Duna", "Frank Herbert", "Ficção Científica", 1965, "https://m.media-amazon.com/images/I/81zN7udGRUL._SY466_.jpg"),
        ("Orgulho e Preconceito", "Jane Austen", "Romance", 1813, "https://m.media-amazon.com/images/I/71Q1tPupKjL._SY466_.jpg"),
        ("O Código Da Vinci", "Dan Brown", "Suspense", 2003, "https://m.media-amazon.com/images/I/91Q5dCjc2KL._SY466_.jpg"),
        ("A Culpa é das Estrelas", "John Green", "Romance", 2012, "https://m.media-amazon.com/images/I/71FxgtFTppL._SY466_.jpg"),
        ("Neuromancer", "William Gibson", "Ficção Científica", 1984, "https://m.media-amazon.com/images/I/71bWQJ6hSyL._SY466_.jpg"),
        ("O Hobbit", "J.R.R. Tolkien", "Fantasia", 1937, "https://m.media-amazon.com/images/I/91dSMhdIzTL._SY466_.jpg"),
        ("Fahrenheit 451", "Ray Bradbury", "Ficção Científica", 1953, "https://m.media-amazon.com/images/I/71OFqSRFDgL._SY466_.jpg"),
        ("O Morro dos Ventos Uivantes", "Emily Bronte", "Romance", 1847, "https://cdn2.penguin.com.au/covers/original/9780553212587.jpg"),
        ("O Diário de Bridget Jones", "Helen Fielding", "Romance", 1996, "https://m.media-amazon.com/images/I/81mCz4TXMSL._SY466_.jpg"),
        ("A Rainha Vermelha", "Victoria Aveyard", "Fantasia", 2015, "https://m.media-amazon.com/images/I/41HQfYIMXzL._SY445_SX342_ML2_.jpg"),
        ("O Ladrão de Almas", "Marco Lago Pereira", "Fantasia", 2015, "https://m.media-amazon.com/images/I/71rDO6D4XIL._SL1500_.jpg"),
        ("Razão e Sensibilidade", "Jane Austen", "Romance", 1811, ""),
        ("Eleanor e Park", "Rainbow Rowell", "Romance", 2012, "https://m.media-amazon.com/images/I/71ix1BMtFlL._SY466_.jpg"),
        ("Jane Eyre", "Charlotte Bronte", "Romance", 1847, "https://m.media-amazon.com/images/I/71kxa1-0mfL._SY466_.jpg"),
        ("P.S. Te Amo", "Cecelia Ahern", "Romance", 2004, "https://m.media-amazon.com/images/I/71x8nO9FCDL._SY466_.jpg"),
        ("Heartstopper", "Alice Oseman", "Romance", 2019, "https://m.media-amazon.com/images/I/71k-7YnXC9L._SY466_.jpg"),
        ("Jogos Vorazes", "Suzanne Collins", "Ficção Científica", 2008, "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgs8JOJtFYBBWsvPl0APGsYVKFeUAWTU_5xnIH8Tb4QPa-NCzLAax5Mab8CFYJwxSxuhGPi52h8alAZLGGrFYzXSM8mZzQBwlQzhw6zPVcRDEzfVJH3Sg9v1p_d9dmBIJUeilJqenYNb_E/s1600/jogos-vorazes-suzanne-collins.jpg"),
        ("Guerra dos Tronos", "George R.R. Martin", "Fantasia", 1996, "https://m.media-amazon.com/images/I/91+1SUO3vUL._SY425_.jpg"),
        ("Alice no País das Maravilhas", "Lewis Carroll", "Fantasia", 1865, "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjcw7LjecrVJx79qGYYt6TXeHYtv6DQzvrgtbBYecNKu4bg0qI8cKHX4Wr1y5Ro5pAlw67w48vRqf68ql-mKofjEeoxujSnvnIgLSVZ4fuvrYZLOPmoaRXAyEbnFxhqEuYsJ7tCATc0/s1600/alice-no-pais-das-maravilhas-lewis-carroll-editora-l-e-pm-colecao-l-e-pm-pocket-2002-capa-livro.jpg"),
        ("Gabriela, Cravo e Canela", "Jorge Amado", "Romance", 1958, "https://m.media-amazon.com/images/I/51+5OgHbwyL._SY445_SX342_ML2_.jpg"),
        ("Como eu era antes de você", "Jojo Moyes", "Romance", 2015, "https://livrariapublica.com.br/capa/como-eu-era-antes-de-voce-jojo-moyes-pdf-B00C9NKYSY.webp"),
        ("Água para elefantes", "Sara Gruen", "Romance", 2006, ""),
        ("Admirável Mundo Novo", "Aldous Huxley", "Ficção Científica", 1932, "https://upload.wikimedia.org/wikipedia/pt/6/62/BraveNewWorld_FirstEdition.jpg"),
        ("A Revolução dos Bichos", "George Orwell", "Ficção Científica", 1945, "https://pt.wikipedia.org/wiki/Animal_Farm#/media/Ficheiro:Animal_Farm_-_1st_edition.jpg"),
        ("Adeus às Armas", "Ernest Hemingway", "Romance", 1929, ""),
        ("Por Quem os Sinos Dobram", "Ernest Hemingway", "Romance", 1940, ""),
        ("Anna Karenina", "Leo Tolstoy", "Romance", 1878, "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/AnnaKareninaTitle.jpg/250px-AnnaKareninaTitle.jpg"),
        ("As Crônicas de Nárnia", "C. S. Lewis", "Fantasia", 1950, "https://en.wikipedia.org/wiki/File:The_Chronicles_of_Narnia_box_set_cover.jpg"),
        ("Moby Dick", "Herman Melville", "Aventura", 1851, "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1605824499i/55953683.jpg"),
        ("As Aventuras de Tom Sawyer", "Mark Twain", "Aventura", 1876, "https://m.media-amazon.com/images/I/71R0rJC6BcL._SY466_.jpg"),
        ("O Livro da Selva", "Rudyard Kipling", "Aventura", 1894, "https://m.media-amazon.com/images/I/515+QPys8OL._SY445_SX342_ML2_.jpg"),
        ("A pequena livraria dos sonhos", "Jenny Colgan", "Romance", 2019, "https://m.media-amazon.com/images/I/61irAkaOOdL._SY425_.jpg"),
        ("Melhor que nos filmes", "Lynn Painter", "Romance", 2023, "https://m.media-amazon.com/images/I/61y5iLUKS3L._SY466_.jpg"),
        ("A Biblioteca da Meia-Noite", "Matt Haig", "Romance", 2021, "https://m.media-amazon.com/images/I/81iqH8dpjuL._SY425_.jpg"),
        ("O Jardim Secreto", "Frances Hodgson Burnett", "Fantasia", 1911, "https://m.media-amazon.com/images/I/71dl7YTMkJL._SY425_.jpg"),
        ("A cabeça do santo", "Socorro Accioli", "Fantasia", 2014, "https://m.media-amazon.com/images/I/71-YhujYUxS._SY466_.jpg"),
        ("Quarta asa", "Rebecca Yarros", "Fantasia", 2024, "https://m.media-amazon.com/images/I/71pSq7HXJ0L._SY342_.jpg"),
        ("O massacre da família Hope", "Riley Sager", "Ficção Científica", 2024, "https://m.media-amazon.com/images/I/815bfY-u6-L._SY466_.jpg"),
        ("O guia definitivo do mochileiro das galáxias", "Douglas Adams", "Ficção Científica", 1979, "https://m.media-amazon.com/images/I/81zQDb6GMVL._SY425_.jpg"),
        ("Jurassic Park", "Michael Crichton", "Ficção Científica", 1990, "https://m.media-amazon.com/images/I/71iiQ6fWLFL._SY522_.jpg"),
        ("O Homem do Castelo Alto", "Philip K. Dick", "Ficção Científica", 1962, "https://m.media-amazon.com/images/I/71XIOHhYu4L._SY466_.jpg"),
        ("Laranja Mecânica", "Anthony Burgess", "Ficção Científica", 1962, "https://m.media-amazon.com/images/I/51cFreMs86L._SY445_SX342_ML2_.jpg"),
        ("A Ilha do Tesouro", "Robert Louis Stevenson", "Aventura", 1883, ""),
        ("Viagens de Gulliver", "Jonathan Swift", "Aventura", 1726, "https://m.media-amazon.com/images/I/81GgLnG0kHL._SY425_.jpg"),
        ("A Máquina do Tempo", "H.G. Wells", "Ficção Científica", 1895, "https://m.media-amazon.com/images/I/71cL9wegDQL._SY466_.jpg"),
        ("O cavaleiro preso na armadura", "Robert Fisher", "Aventura", 2006, "https://m.media-amazon.com/images/I/91of8o2YfpL._SY466_.jpg"),
        ("O Nome do Vento", "Patrick Rothfuss", "Fantasia", 2007, "https://m.media-amazon.com/images/I/81CGmkRG9GL.jpg"),
        ("Sombra e Ossos", "Leigh Bardugo", "Fantasia", 2012, "https://m.media-amazon.com/images/I/511uE-QpfEL._SY445_SX342_QL70_ML2_.jpg")
    ]

    livro_ids = []
    for titulo, autor, genero, ano, img_url in livros_data:
        lid = str(uuid.uuid4())
        bd.cadastrarLivro(lid, titulo, autor, genero, ano, img_url)
        livro_ids.append(lid)

    print(f"✓ {len(livro_ids)} livros criados\n")

    # Leituras com avaliações - EXPANDIDO PARA 150+
    print("📚 Adicionando leituras com avaliações...\n")

    # Cada usuário vai avaliar entre 8-12 livros
    avaliacoes_por_usuario = {
        # Perfis de preferência
        0: {  # Maria - Ficção Científica
            "livros": [0, 3, 7, 9, 19, 25, 26, 41, 43, 45],
            "notas": [9.0, 8.5, 8.0, 8.5, 9.0, 8.0, 8.5, 9.0, 8.0, 7.5]
        },
        1: {  # João - Fantasia
            "livros": [1, 2, 8, 12, 13, 20, 33, 40, 48, 49],
            "notas": [9.5, 9.0, 8.5, 8.0, 8.5, 9.0, 7.5, 8.5, 9.0, 8.5]
        },
        2: {  # Ana - Romance
            "livros": [4, 6, 10, 11, 15, 16, 18, 22, 23, 24],
            "notas": [9.0, 8.5, 8.0, 7.5, 8.5, 9.0, 8.0, 8.5, 9.0, 8.5]
        },
        3: {  # Joana - Ficção Científica
            "livros": [0, 3, 7, 9, 19, 25, 26, 41, 43, 45],
            "notas": [8.5, 8.0, 7.5, 8.0, 8.5, 7.5, 8.0, 8.5, 7.5, 7.0]
        },
        4: {  # Miriam - Romance
            "livros": [4, 6, 10, 11, 15, 16, 17, 22, 23, 24],
            "notas": [8.0, 8.5, 8.0, 8.5, 9.0, 8.5, 8.0, 8.0, 8.5, 7.5]
        },
        5: {  # José - Aventura
            "livros": [34, 35, 36, 37, 44, 47, 50, 8, 1, 20],
            "notas": [9.0, 8.5, 8.0, 9.0, 8.5, 8.0, 8.5, 8.0, 7.5, 8.0]
        },
        6: {  # Karen - Romance
            "livros": [4, 6, 11, 15, 16, 18, 22, 23, 24, 38],
            "notas": [8.5, 8.0, 7.5, 8.0, 8.5, 8.0, 8.5, 9.0, 8.0, 8.5]
        },
        7: {  # Alan - Ficção Científica
            "livros": [0, 3, 7, 9, 19, 25, 26, 41, 42, 43],
            "notas": [8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.0, 8.5, 8.0]
        },
        8: {  # Bruno - Fantasia
            "livros": [1, 2, 8, 12, 13, 20, 33, 40, 48, 49],
            "notas": [8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0]
        },
        9: {  # Juliana - Romance
            "livros": [4, 6, 10, 11, 15, 16, 18, 22, 23, 24],
            "notas": [9.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 9.0, 8.0]
        },
        10: {  # Arthur - Ficção Científica
            "livros": [0, 3, 7, 9, 19, 25, 26, 41, 42, 45],
            "notas": [8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0]
        },
        11: {  # Amanda - Romance
            "livros": [4, 6, 11, 15, 16, 17, 22, 23, 24, 38],
            "notas": [8.0, 8.5, 8.0, 8.5, 9.0, 8.0, 8.5, 8.0, 8.5, 8.0]
        },
        12: {  # Paulo - Fantasia
            "livros": [1, 2, 8, 12, 13, 20, 33, 40, 48, 49],
            "notas": [8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0]
        },
        13: {  # Ana Paula - Romance
            "livros": [4, 6, 10, 11, 15, 16, 18, 22, 23, 24],
            "notas": [8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 9.0, 8.0, 8.5]
        },
        14: {  # Daniel - Ficção Científica
            "livros": [0, 3, 7, 9, 19, 25, 26, 41, 43, 45],
            "notas": [8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5]
        },
        15: {  # Larissa - Romance
            "livros": [4, 6, 11, 15, 16, 17, 22, 23, 24, 38],
            "notas": [8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0]
        },
        16: {  # Luís - Aventura
            "livros": [34, 35, 36, 37, 44, 47, 50, 8, 1, 20],
            "notas": [8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5]
        },
        17: {  # Silvia - Romance
            "livros": [4, 6, 10, 11, 15, 16, 18, 22, 23, 24],
            "notas": [8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0]
        },
        18: {  # Alexandre - Ficção Científica
            "livros": [0, 3, 7, 9, 19, 25, 26, 41, 42, 43],
            "notas": [8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5]
        },
        19: {  # César - Fantasia
            "livros": [1, 2, 8, 12, 13, 20, 33, 40, 48, 49],
            "notas": [8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0]
        },
        20: {  # Cássia - Romance
            "livros": [4, 6, 11, 15, 16, 17, 22, 23, 24, 38],
            "notas": [8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5]
        },
        21: {  # Clara - Romance
            "livros": [4, 6, 10, 11, 15, 16, 18, 22, 23, 24],
            "notas": [8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0]
        },
        22: {  # Marisa - Romance
            "livros": [4, 6, 11, 15, 16, 17, 22, 23, 24, 38],
            "notas": [8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5]
        },
        23: {  # Roberto - Ficção Científica
            "livros": [0, 3, 7, 9, 19, 25, 26, 41, 43, 45],
            "notas": [8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0]
        },
        24: {  # Eduardo - Fantasia
            "livros": [1, 2, 8, 12, 13, 20, 33, 40, 48, 49],
            "notas": [8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5, 8.0, 8.5]
        },
    }

    total_avaliacoes = 0
    for usuario_idx, prefs in avaliacoes_por_usuario.items():
        for livro_idx, nota in zip(prefs["livros"], prefs["notas"]):
            bd.cadastrarLeitura(usuario_ids[usuario_idx], livro_ids[livro_idx], "lido", nota, "2024-01-15", "")
            total_avaliacoes += 1

    print("\n✅ Seed concluído com sucesso!")
    print(f"📊 RESUMO:")
    print(f"   - Usuários: {len(usuario_ids)}")
    print(f"   - Livros: {len(livro_ids)}")
    print(f"   - Leituras: {total_avaliacoes}")


if __name__ == "__main__":
    popular_banco_teste()