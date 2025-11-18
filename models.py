import uuid
import bcrypt

class Livro:
    def __init__(self, titulo, autor, genero, ano_publicacao, imagem_url=None): # Modificação em colocar a url
        self.id = str(uuid.uuid4())
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.ano_publicacao = ano_publicacao
        self.imagem_url = imagem_url

class Usuario:
    def __init__(self, nome, email, senha=None, data_nasc=None, senha_hash=None):
        self.id = str(uuid.uuid4())  # IDs aleatórios e seguros
        self.nome = nome
        self.email = email
        self.data_nasc = data_nasc
        self.leituras = []  # Array de leituras

        # Se vier o hash do banco = usa diretamente
        if senha_hash is not None:
            self._senha_hash = senha_hash

        # Se for criação normal = criptografa a senha
        else:
            if senha is None:
                raise ValueError("Senha é obrigatória para novos usuários.")
            self._senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

    def registrarLeitura(self, livro, status, avaliacao, data_leitura):
        leitura = Leitura(self.id, livro.id, status, avaliacao, data_leitura)
        self.leituras.append(leitura) # Armazenar leitura no array

    def verificar_senha(self, senha): # Validação para senha criptografada :)
        return bcrypt.checkpw(senha.encode(), self._senha_hash)

    # Função pra omitirmos a senha no json
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "data_nasc": self.data_nasc
        }

class Leitura:
    def __init__(self, idUsuario, idLivro, status, avaliacao=None, dataLeitura=None, comentario=None):
        self.id_usuario = idUsuario
        self.id_livro = idLivro
        self.status = status # ex: "lido", "lendo", "quero ler"
        self.avaliacao = avaliacao # nota opcional
        self.dataLeitura = dataLeitura
        self.comentario = comentario
