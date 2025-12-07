import os
import uuid
import psycopg
from dotenv import load_dotenv

load_dotenv()

from models import Livro, Usuario, Leitura


def get_connection():
    url = os.getenv("DATABASE_URL")

    if not url:
        raise Exception("DATABASE_URL não encontrada no ambiente (.env)")

    if "railway" in url:
        return psycopg.connect(url, sslmode="require")

    return psycopg.connect(url, sslmode="disable")


def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de livros com campos de aprovação
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id TEXT PRIMARY KEY,
            titulo VARCHAR NOT NULL, 
            autor VARCHAR NOT NULL,
            genero VARCHAR NOT NULL,
            ano_publicacao INT NOT NULL,
            imagem_url TEXT,
            status_aprovacao VARCHAR(20) DEFAULT 'pendente',
            cadastrado_por TEXT,
            data_aprovacao TIMESTAMP,
            aprovado_por TEXT,
            motivo_rejeicao TEXT
        );
    ''')

    # Tabela de usuários com role
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            nome VARCHAR NOT NULL,
            email VARCHAR NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            data_nasc DATE NOT NULL,
            role VARCHAR(20) DEFAULT 'usuario'
        );
    ''')

    # Tabela de leituras
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
    # LIVROS
    ############################################

    def carregarLivros(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, titulo, autor, genero, ano_publicacao, imagem_url, 
                   status_aprovacao, cadastrado_por, data_aprovacao, aprovado_por, motivo_rejeicao 
            FROM livros
        """)

        for row in cursor.fetchall():
            livro = Livro(
                titulo=row[1],
                autor=row[2],
                genero=row[3],
                ano_publicacao=row[4],
                imagem_url=row[5],
                status_aprovacao=row[6] or 'pendente',
                cadastrado_por=row[7],
                data_aprovacao=row[8],
                aprovado_por=row[9],
                motivo_rejeicao=row[10]
            )
            livro.id = row[0]
            self.livros[livro.id] = livro

        cursor.close()
        conn.close()

    def buscarTodosLivros(self):
        """Retorna apenas livros aprovados (para o catálogo público)."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, titulo, autor, genero, ano_publicacao, imagem_url, status_aprovacao
            FROM livros 
            WHERE status_aprovacao = 'aprovado'
            ORDER BY titulo
        """)

        livros = []
        for row in cursor.fetchall():
            livro = Livro(
                titulo=row[1],
                autor=row[2],
                genero=row[3],
                ano_publicacao=row[4],
                imagem_url=row[5],
                status_aprovacao=row[6]
            )
            livro.id = row[0]
            livros.append(livro)

        cursor.close()
        conn.close()
        return livros

    def cadastrarLivro(self, id, titulo, autor, genero, ano_publicacao, imagem_url=None, cadastrado_por=None):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO livros (id, titulo, autor, genero, ano_publicacao, imagem_url, status_aprovacao, cadastrado_por)
            VALUES (%s, %s, %s, %s, %s, %s, 'pendente', %s)
        """, (id, titulo, autor, genero, ano_publicacao, imagem_url, cadastrado_por))

        conn.commit()
        cursor.close()
        conn.close()

        livro = Livro(titulo, autor, genero, ano_publicacao, imagem_url,
                      status_aprovacao='pendente', cadastrado_por=cadastrado_por)
        livro.id = id
        self.livros[id] = livro
        return livro

    def editarLivro(self, id, titulo, autor, genero, ano_publicacao, imagem_url=None):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE livros SET titulo = %s, autor = %s, genero = %s, 
                              ano_publicacao = %s, imagem_url = %s 
            WHERE id = %s
        """, (titulo, autor, genero, ano_publicacao, imagem_url, id))

        conn.commit()
        cursor.close()
        conn.close()

        if id in self.livros:
            livro = self.livros[id]
            livro.titulo = titulo
            livro.autor = autor
            livro.genero = genero
            livro.ano_publicacao = ano_publicacao
            livro.imagem_url = imagem_url
            return livro

        livro = Livro(titulo, autor, genero, ano_publicacao, imagem_url)
        livro.id = id
        return livro

    def buscarLivroPorId(self, livro_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, titulo, autor, genero, ano_publicacao, imagem_url, 
                   status_aprovacao, cadastrado_por, data_aprovacao, aprovado_por, motivo_rejeicao
            FROM livros WHERE id = %s
        """, (livro_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            livro = Livro(
                titulo=row[1],
                autor=row[2],
                genero=row[3],
                ano_publicacao=row[4],
                imagem_url=row[5],
                status_aprovacao=row[6],
                cadastrado_por=row[7],
                data_aprovacao=row[8],
                aprovado_por=row[9],
                motivo_rejeicao=row[10]
            )
            livro.id = row[0]
            return livro
        return None

    def excluirLivro(self, livro_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM livros WHERE id = %s RETURNING id;", (livro_id,))
        row = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if row:
            if livro_id in self.livros:
                del self.livros[livro_id]
            return True
        return False

    ############################################
    # USUARIOS
    ############################################

    def carregarUsuarios(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome, email, senha, data_nasc, role FROM usuarios")

        for row in cursor.fetchall():
            senha_db = row[3]
            if isinstance(senha_db, str):
                senha_db = senha_db.encode()

            usuario = Usuario(
                nome=row[1],
                email=row[2],
                senha_hash=senha_db,
                data_nasc=row[4],
                role=row[5] or 'usuario'
            )
            usuario.id = row[0]
            self.usuarios[usuario.id] = usuario

        cursor.close()
        conn.close()

    def cadastrarUsuario(self, id, nome, email, senha, data_nasc, role='usuario'):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existente = cursor.fetchone()

        if existente:
            cursor.close()
            conn.close()
            return None

        usuario = Usuario(nome, email, senha, data_nasc, role=role)
        usuario.id = id  # Usa o ID passado

        senha_str = usuario._senha_hash
        if isinstance(senha_str, bytes):
            senha_str = senha_str.decode()

        cursor.execute("""
            INSERT INTO usuarios (id, nome, email, senha, data_nasc, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario.id, nome, email, senha_str, data_nasc, role))

        conn.commit()
        cursor.close()
        conn.close()

        self.usuarios[usuario.id] = usuario
        return usuario

    def buscarEmail(self, email):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, senha, data_nasc, role 
            FROM usuarios 
            WHERE email = %s
        """, (email,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            senha_db = row[3]
            if isinstance(senha_db, str):
                senha_db = senha_db.encode()

            usuario = Usuario(
                nome=row[1],
                email=row[2],
                senha_hash=senha_db,
                data_nasc=row[4],
                role=row[5] or 'usuario'
            )
            usuario.id = row[0]
            self.usuarios[usuario.id] = usuario
            return usuario

        return None

    ############################################
    # LEITURAS
    ############################################

    def carregarLeituras(self, idUsuario):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, id_usuario, id_livro, status, avaliacao, data_leitura, comentario
            FROM leituras
            WHERE id_usuario = %s
        """, (idUsuario,))

        leituras = [Leitura.from_row(row) for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return leituras

    def carregarTodasLeituras(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, id_usuario, id_livro, status, avaliacao, data_leitura, comentario
            FROM leituras
        """)

        leituras = [Leitura.from_row(row) for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return leituras

    def cadastrarLeitura(self, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario):
        conn = get_connection()
        cursor = conn.cursor()

        leitura = Leitura(idUsuario, idLivro, status, avaliacao, dataLeitura, comentario)

        cursor.execute("""
            INSERT INTO leituras 
            (id, id_usuario, id_livro, status, avaliacao, data_leitura, comentario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (leitura.id, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario))

        conn.commit()
        cursor.close()
        conn.close()

        return leitura

    def editarLeitura(self, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE leituras 
            SET status = %s, avaliacao = %s, data_leitura = %s, comentario = %s
            WHERE id_usuario = %s AND id_livro = %s
            RETURNING id;
        """, (status, avaliacao, dataLeitura, comentario, idUsuario, idLivro))

        row = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if row:
            return Leitura(idUsuario, idLivro, status, avaliacao, dataLeitura, comentario, id=row[0])
        return None

    def deletarLeitura(self, idUsuario, idLivro):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM leituras 
            WHERE id_usuario = %s AND id_livro = %s
            RETURNING id;
        """, (idUsuario, idLivro))

        row = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return row is not None


bd = BancoDados()