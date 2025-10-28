import sqlite3

from models import Livro, Usuario, Leitura


def criar_tabelas(db_path='projeto_acervo'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Como não foi feito antes a adição da url então tive que alterar a tabela
    try:
        cursor.execute("ALTER TABLE livros ADD COLUMN imagem_url TEXT")
    except sqlite3.OperationalError:
        # coluna já existe
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id TEXT PRIMARY KEY NOT NULL,
            titulo VARCHAR NOT NULL,
            autor VARCHAR NOT NULL,
            genero VARCHAR NOT NULL,
            ano_publicacao INT NOT NULL,
            imagem_url TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY NOT NULL,
            nome VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            senha TEXT NOT NULL,
            data_nasc DATE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id_usuario TEXT NOT NULL,
            id_livro TEXT NOT NULL,
            status TEXT NOT NULL,
            avaliacao REAL,
            data_leitura DATE,
            comentario TEXT,
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
            FOREIGN KEY (id_livro) REFERENCES livros (id),
            PRIMARY KEY (id_usuario, id_livro)
        )
    ''')

    conn.commit()
    conn.close()

class BancoDados:
    def __init__(self, db_path='projeto_acervo'):
        self.db_path = db_path
        criar_tabelas(self.db_path)
        self.livros = {}
        self.usuarios = {}
        self.carregarDados()

    def carregarDados(self):
        self.carregarLivros()
        self.carregarUsuarios()

############################################
        ########## LIVROS ##########
            ####################

    def carregarLivros(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Carregar os livros
        cursor.execute("SELECT id, titulo, autor, genero, ano_publicacao FROM livros")
        for row in cursor.fetchall():
            livro = Livro(row[1], row[2], row[3], row[4])
            livro.id = row[0]
            self.livros[livro.id] = livro

        conn.close()

    def cadastrarLivro(self, id, titulo, autor, genero, ano_publicacao,  imagem_url=None):
        livro = Livro(titulo, autor, genero, ano_publicacao, imagem_url)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO livros (id, titulo, autor, genero, ano_publicacao, imagem_url) VALUES (?, ?, ?, ?, ?, ?)",
            (id, titulo, autor, genero, ano_publicacao, imagem_url)
        )

        conn.commit()
        conn.close()
        self.livros[livro.id] = livro

        return livro

    def editarLivro(self, id, titulo, autor, genero, ano_publicacao):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE livros SET titulo = ?, autor = ?, genero = ?, ano_publicacao = ? WHERE id = ?",
            (titulo, autor, genero, ano_publicacao, id)
        )

        conn.commit()

        livro = Livro(titulo, autor, genero, ano_publicacao)
        livro.id = id           # Vamos garantir que o id se manterá o mesmo
        self.livros[id] = livro
        conn.close()
        return livro

############################################
        ########## USUARIOS ##########
            ####################

    def carregarUsuarios(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome, email, senha, data_nasc FROM usuarios")
        for row in cursor.fetchall():
            usuario = Usuario(row[1], row[2], row[3], row[4])
            usuario.id = row[0]
            self.usuarios[usuario.id] = usuario

        conn.close()

    def cadastrarUsuario(self, id, nome, email, senha, data_nasc):
        usuario = Usuario(nome, email, senha, data_nasc)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (id, nome, email, senha, data_nasc) VALUES (?, ?, ?, ?, ?)",
            (id, nome, email, senha, data_nasc)
        )

        conn.commit()

        self.usuarios[usuario.id] = usuario
        conn.close()
        return usuario

    def buscarEmail(self, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome, email, senha, data_nasc FROM usuarios WHERE email = ?",
                       (email,))
        row = cursor.fetchone() # Registramos a coluna com o que foi encontrado (ou retorna null :p)

        if row: # Caso seja encontrado, registra o usuário para retorná-lo
            usuario = Usuario(row[1], row[2], row[3], row[4])
            usuario.id = row[0]
            # Retornamos usuario para validação
            return usuario

        conn.close()
        return None

############################################
        ########## LEITURAS ##########
            ####################

    def carregarLeituras(self, idUsuario):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id_usuario, id_livro, status, avaliacao, data_leitura, comentario FROM leituras where id_usuario = ?",
             (idUsuario,))

        leituras = [] # Abrimos um array
        for row in cursor.fetchall():
            leitura = Leitura(row[0], row[1], row[2], row[3], row[4], row[5])
            leituras.append(leitura) # Registramos cada uma das leituras do loop dentro do array
            return leituras

        conn.close()
        return None

    def cadastrarLeitura(self, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO leituras (id_usuario, id_livro, status, avaliacao, data_leitura, comentario) VALUES (?, ?, ?, ?, ?)",
            (idUsuario, idLivro, status, avaliacao, dataLeitura)
        )
        conn.commit()
        conn.close()

        nova_leitura = Leitura(idUsuario, idLivro, status, avaliacao, dataLeitura, comentario)
        return nova_leitura

    def editarLeitura(self, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE leituras SET status = ?, avaliacao = ?, data_leitura = ?, comentario = ? WHERE id_usuario = ? AND id_livro = ?",
                (status, avaliacao, dataLeitura, comentario, idUsuario, idLivro)
        )
        conn.commit()
        conn.close()

        leitura = Leitura(idUsuario, idLivro, status, avaliacao, dataLeitura)
        return leitura
############################################