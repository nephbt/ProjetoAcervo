import sqlite3
import uuid
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

    # Caso você ainda estiver com a tabela de leituras antiga ativa essa linha e executa, dpa apaga. cursor.execute("DROP TABLE IF EXISTS leituras")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id TEXT PRIMARY KEY NOT NULL,
            id_usuario TEXT NOT NULL,
            id_livro TEXT NOT NULL,
            status TEXT NOT NULL,
            avaliacao REAL,
            data_leitura DATE,
            comentario TEXT,
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
            FOREIGN KEY (id_livro) REFERENCES livros (id)
        )
    ''')

    conn.commit()
    conn.close()

def criar_backup(db_path='projeto_acervo', backup_path='backup.sql'):
    conn = sqlite3.connect(db_path)
    with open(backup_path, "w", encoding="utf-8") as f:
        for line in conn.iterdump():
            f.write("%s\n" % line)
    conn.close()
    print(f"Backup criado com sucesso em {backup_path}")

def restaurar_backup(db_path='projeto_acervo', backup_path='backup.sql'):
    conn = sqlite3.connect(db_path)
    with open(backup_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()
    print(f"Banco restaurado a partir de {backup_path}")


class BancoDados:
    def __init__(self, db_path='projeto_acervo'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)  # 👈 ADICIONE ESTA LINHA
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

        cursor.execute("SELECT id, titulo, autor, genero, ano_publicacao, imagem_url FROM livros")
        for row in cursor.fetchall():
            livro = Livro(row[1], row[2], row[3], row[4], row[5])  # inclui imagem_url
            livro.id = row[0]
            self.livros[livro.id] = livro

        conn.close()


    def cadastrarLivro(self, id, titulo, autor, genero, ano_publicacao, imagem_url):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO livros (id, titulo, autor, genero, ano_publicacao, imagem_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, titulo, autor, genero, ano_publicacao, imagem_url))

        conn.commit()
        conn.close()

        livro = Livro(titulo, autor, genero, ano_publicacao, imagem_url)
        livro.id = id
        self.livros[id] = livro  # Atualiza o cache em memória
        return livro

    def editarLivro(self, id, titulo, autor, genero, ano_publicacao, imagem_url=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE livros SET titulo = ?, autor = ?, genero = ?, ano_publicacao = ?, imagem_url = ? WHERE id = ?",
            (titulo, autor, genero, ano_publicacao, imagem_url, id)
        )

        conn.commit()

        # Atualiza no cache (dicionário em memória)
        livro = Livro(titulo, autor, genero, ano_publicacao, imagem_url=imagem_url)
        livro.id = id
        self.livros[id] = livro

        conn.close()
        return livro

    
    def buscarLivroPorId(self, livro_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livros WHERE id = ?", (livro_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            livro = Livro(row[1], row[2], row[3], row[4], row[5])
            livro.id = row[0]
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
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            existente = cursor.fetchone()

            if existente:
                conn.close()
                # retorna None indicando que já existe
                return None

            usuario = Usuario(nome, email, senha, data_nasc)

            cursor.execute(
                "INSERT INTO usuarios (id, nome, email, senha, data_nasc) VALUES (?, ?, ?, ?, ?)",
                (id, nome, email, senha, data_nasc)
            )

        self.usuarios[usuario.id] = usuario
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
            "SELECT id_usuario, id_livro, status, avaliacao, data_leitura, comentario FROM leituras WHERE id_usuario = ?",
            (idUsuario,)
        )

        leituras = []
        for row in cursor.fetchall():
            leitura = Leitura(row[0], row[1], row[2], row[3], row[4], row[5])
            leituras.append(leitura)

        conn.close()
        return leituras

    
    def cadastrarLeitura(self, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        leitura_id = str(uuid.uuid4())

        cursor.execute(
            "INSERT INTO leituras (id, id_usuario, id_livro, status, avaliacao, data_leitura, comentario) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (leitura_id, idUsuario, idLivro, status, avaliacao, dataLeitura, comentario)
        )

        conn.commit()
        conn.close()

        nova_leitura = Leitura(idUsuario, idLivro, status, avaliacao, dataLeitura, comentario)
        nova_leitura.id = leitura_id
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
    
        
bd = BancoDados()  # instância única para toda a aplicação
############################################