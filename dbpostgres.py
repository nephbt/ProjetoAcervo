{"id":"81291","variant":"standard","title":"database.py reestruturado para PostgreSQL (Railway)"}
import os
import uuid
import psycopg2
from dotenv import load_dotenv
load_dotenv()
from psycopg2.extras import RealDictCursor
from models import Livro, Usuario, Leitura


def get_connection():
    url = os.environ["DATABASE_URL"]

    # Railway sempre precisa de SSL
    if "railway" in url or "internal" in url:
        return psycopg2.connect(url, sslmode="require")

    # Local (GitHub Actions, sua máquina): sem SSL
    return psycopg2.connect(url, sslmode="disable")


def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id TEXT PRIMARY KEY,
            titulo VARCHAR NOT NULL, 
            autor VARCHAR NOT NULL,
            genero VARCHAR NOT NULL,
            ano_publicacao INT NOT NULL,
            imagem_url TEXT
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            nome VARCHAR NOT NULL,
            email VARCHAR NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            data_nasc DATE NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id TEXT PRIMARY KEY,
            id_usuario TEXT NOT NULL REFERENCES usuarios(id),
            id_livro TEXT NOT NULL REFERENCES livros(id),
            status TEXT NOT NULL,
            avaliacao REAL,
            data_leitura DATE,
            comentario TEXT
        );
    ''')

    conn.commit()
    cursor.close()
    conn.close()



class BancoDados:
    def __init__(self):
        criar_tabelas()
        self.livros = {}
        self.usuarios = {}
        self.carregarDados()


    def carregarDados(self):
        self.carregarLivros()
        self.carregarUsuarios()

    ############################################
    ########## LIVROS ##########
    ############################################

    def carregarLivros(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, titulo, autor, genero, ano_publicacao, imagem_url FROM livros")

        for row in cursor.fetchall():
            livro = Livro(row[1], row[2], row[3], row[4], row[5])
            livro.id = row[0]
            self.livros[livro.id] = livro

        cursor.close()
        conn.close()


    def cadastrarLivro(self, id, titulo, autor, genero, ano_publicacao, imagem_url):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO livros (id, titulo, autor, genero, ano_publicacao, imagem_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id, titulo, autor, genero, ano_publicacao, imagem_url))

        conn.commit()
        cursor.close()
        conn.close()

        livro = Livro(titulo, autor, genero, ano_publicacao, imagem_url)
        livro.id = id
        self.livros[id] = livro
        return livro


    def editarLivro(self, id, titulo, autor, genero, ano_publicicao, imagem_url=None):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE livros SET titulo = %s, autor = %s, genero = %s, 
                              ano_publicacao = %s, imagem_url = %s 
            WHERE id = %s
        """, (titulo, autor, genero, ano_publicicao, imagem_url, id))

        conn.commit()
        cursor.close()
        conn.close()

        livro = Livro(titulo, autor, genero, ano_publicicao, imagem_url)
        livro.id = id
        self.livros[id] = livro
        return livro


    def buscarLivroPorId(self, livro_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM livros WHERE id = %s", (livro_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            livro = Livro(row[1], row[2], row[3], row[4], row[5])
            livro.id = row[0]
            return livro


    ############################################
    ########## USUARIOS ##########
    ############################################

    def carregarUsuarios(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome, email, data_nasc FROM usuarios")

        for row in cursor.fetchall():
            usuario = Usuario(
                nome=row[1],
                email=row[2],
                senha="",
                data_nasc=row[3]
            )
            usuario.id = row[0]
            usuario._senha_hash = None
            self.usuarios[usuario.id] = usuario

        cursor.close()
        conn.close()


    def cadastrarUsuario(self, nome, email, senha, data_nasc):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existente = cursor.fetchone()

        if existente:
            cursor.close()
            conn.close()
            return None

        usuario = Usuario(nome, email, senha, data_nasc)

        cursor.execute("""
            INSERT INTO usuarios (id, nome, email, senha, data_nasc)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario.id, nome, email, usuario._senha_hash.decode(), usuario.data_nasc))

        conn.commit()
        cursor.close()
        conn.close()

        self.usuarios[usuario.id] = usuario
        return usuario


    def buscarEmail(self, email):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, senha, data_nasc 
            FROM usuarios 
            WHERE email = %s
        """, (email,))

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            usuario = Usuario(
                nome=row[1],
                email=row[2],
                senha_hash=row[3].encode(),
                data_nasc=row[4]
            )
            usuario.id = row[0]
            self.usuarios[usuario.id] = usuario
            return usuario

        return None


    ############################################
    ########## LEITURAS ##########
    ############################################

    def carregarLeituras(self, idUsuario):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_usuario, id_livro, status, avaliacao, data_leitura, comentario
            FROM leituras
            WHERE id_usuario = %s
        """, (idUsuario,))

        leituras = []
        for row in cursor.fetchall():
            leitura = Leitura(row[0], row[1], row[2], row[3], row[4], row[5])
            leituras.append(leitura)

        cursor.close()
        conn.close()
        return leituras


    def cadastrarLeitura(self, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario):
        conn = get_connection()
        cursor = conn.cursor()

        leitura_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO leituras 
            (id, id_usuario, id_livro, status, avaliacao, data_leitura, comentario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (leitura_id, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario))

        conn.commit()
        cursor.close()
        conn.close()

        nova = Leitura(idUsuario, idLivro, status, avaliacao, dataLeitura, comentario)
        nova.id = leitura_id
        return nova


    def editarLeitura(self, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE leituras SET status = %s, avaliacao = %s, data_leitura = %s, comentario = %s
            WHERE id_usuario = %s AND id_livro = %s
        """, (status, avaliacao, dataLeitura, comentario, idUsuario, idLivro))

        conn.commit()
        cursor.close()
        conn.close()

        leitura = Leitura(idUsuario, idLivro, status, avaliacao, dataLeitura)
        return leitura


bd = BancoDados()
