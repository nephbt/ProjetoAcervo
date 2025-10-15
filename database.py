import sqlite3

from models import Livro, Usuario, Leitura


def criar_tabelas(db_path='projeto_acervo'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id TEXT PRIMARY KEY NOT NULL,
            titulo VARCHAR NOT NULL,
            autor VARCHAR NOT NULL,
            genero VARCHAR NOT NULL,
            ano_publicacao INT NOT NULL
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

    def adicionarLivro(self, id, titulo, autor, genero, ano_publicacao):
        livro = Livro(titulo, autor, genero, ano_publicacao)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO livros (id, titulo, autor, genero, ano_publicacao) VALUES (?, ?, ?, ?, ?)",
            (id, titulo, autor, genero, ano_publicacao)
        )

        conn.commit()
        conn.close()

        self.livros[livro.id] = livro
        return livro

############################################
        ########## USUARIOS ##########
            ####################

    def carregarUsuarios(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Carregar os usuários
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
            "INSERT INTO livros (id, nome, email, senha, data_nasc) VALUES (?, ?, ?, ?, ?)",
            (id, nome, email, senha, data_nasc)
        )

        conn.commit()
        conn.close()

        self.usuarios[usuario.id] = usuario
        return usuario

    def buscarEmail(self, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome, email, senha, data_nasc FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            usuario = Usuario(row[1], row[2], row[3], row[4])
            usuario.id = row[0]
            # Retornamos usuario para validação
            return usuario
        return None

############################################

