import uuid
import bcrypt


class Livro:
    def __init__(self, titulo, autor, genero, ano_publicacao, imagem_url=None,
                 status_aprovacao="pendente", cadastrado_por=None,
                 data_aprovacao=None, aprovado_por=None, motivo_rejeicao=None):
        self.id = str(uuid.uuid4())
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.ano_publicacao = ano_publicacao
        self.imagem_url = imagem_url  # ← Corrigido!
        self.status_aprovacao = status_aprovacao
        self.cadastrado_por = cadastrado_por
        self.data_aprovacao = data_aprovacao
        self.aprovado_por = aprovado_por
        self.motivo_rejeicao = motivo_rejeicao

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero,
            "ano_publicacao": self.ano_publicacao,
            "imagem": self.imagem_url,
            "imagem_url": self.imagem_url,
            "status_aprovacao": self.status_aprovacao,
            "cadastrado_por": self.cadastrado_por,
            "data_aprovacao": str(self.data_aprovacao) if self.data_aprovacao else None,
            "motivo_rejeicao": self.motivo_rejeicao
        }


class Usuario:
    def __init__(self, nome, email, senha=None, data_nasc=None,
                 senha_hash=None, role="usuario"):
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.email = email
        self.data_nasc = data_nasc
        self.role = role

        if senha_hash:
            self._senha_hash = senha_hash
        elif senha:
            self._senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        else:
            self._senha_hash = None

    @property
    def senha(self):
        return self._senha_hash

    def verificar_senha(self, senha_texto):
        if not self._senha_hash:
            return False
        senha_hash = self._senha_hash
        if isinstance(senha_hash, str):
            senha_hash = senha_hash.encode('utf-8')
        return bcrypt.checkpw(senha_texto.encode('utf-8'), senha_hash)

    def is_admin(self):
        return self.role == "admin"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "data_nasc": str(self.data_nasc) if self.data_nasc else None,
            "role": self.role
        }


class Leitura:
    def __init__(self, id_usuario, id_livro, status, avaliacao, data_leitura, comentario, id=None):
        self.id = id if id else str(uuid.uuid4())
        self.id_usuario = id_usuario
        self.id_livro = id_livro
        self.status = status
        self.avaliacao = avaliacao
        self.dataLeitura = data_leitura
        self.data_leitura = data_leitura
        self.comentario = comentario

    def to_dict(self):
        return {
            "id": self.id,
            "id_usuario": self.id_usuario,
            "id_livro": self.id_livro,
            "status": self.status,
            "avaliacao": self.avaliacao,
            "data_leitura": str(self.data_leitura) if self.data_leitura else None,
            "dataLeitura": str(self.dataLeitura) if self.dataLeitura else None,
            "comentario": self.comentario
        }

    @staticmethod
    def from_row(row):
        return Leitura(
            id_usuario=row[1],
            id_livro=row[2],
            status=row[3],
            avaliacao=row[4],
            data_leitura=row[5],
            comentario=row[6],
            id=row[0]
        )