import uuid
import bcrypt

class Livro:
    def __init__(self, titulo, autor, genero, ano_publicacao):
        self.id = str(uuid.uuid4()) # Vamos gerar IDs aleatorios e seguros
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.ano_publicacao = ano_publicacao

class Usuario:
    def __init__(self, nome, email, senha, data_nasc):
        self.id = str(uuid.uuid4()) # Vamos gerar IDs aleatorios e seguros
        self.nome = nome
        self.email = email
        self._senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()) # Vamos criptografar a senha do usuário
        self.data_nasc = data_nasc
        self.leituras = [] # Array de leituras

    def registrarLeitura(self, livro, status, avaliacao, data_leitura):
        leitura = Leitura(self.id, livro.id, status, avaliacao, data_leitura)
        self.leituras.append(leitura) # Armazenar leitura no array

    def verificar_senha(self, senha): # Validação para senha criptografada :)
        return bcrypt.checkpw(senha.encode(), self._senha_hash)


    # Omitir senha no json
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "data_nasc": self.data_nasc
        }

class Leitura:
    def __init__(self, id_usuario, id_livro, status, avaliacao=None, data_leitura=None):
        self.id_usuario = id_usuario
        self.id_livro = id_livro
        self.status = status # ex: "lido", "lendo", "quero ler"
        self.avaliacao = avaliacao # nota opcional
        self.data_leitura = data_leitura
