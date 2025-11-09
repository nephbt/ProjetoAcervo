'''
from flask import Blueprint, jsonify, request
from database import BancoDados
from functools import wraps
import uuid
import jwt
import datetime

livrosRoute= Blueprint("livros", __name__, url_prefix="/livros")
usuariosRoute= Blueprint("usuarios", __name__, url_prefix="/usuarios")
leiturasRoute = Blueprint("leituras", __name__, url_prefix="/leituras")
bd = BancoDados()
key = "chave_bem_secreta"

# ---------------- Área dos tokens !! ----------------
def gerar_token(usuario_id):
    """
    Vamos gerar um JWT para o usuário, válido por 2 horas. :)
    """
    payload = {
        "id": usuario_id,
        "exp": datetime.datetime.now() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, key, algorithm="HS256")
    return token

def requerir_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"erro": "Token ausente"}), 401

        try:
            token = token.replace("Bearer ", "")
            decoded = jwt.decode(token, key, algorithms=["HS256"])
            id_usuario = decoded["id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
                                                            # Tratamento de erros
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401

        return f(id_usuario=id_usuario, *args, **kwargs)
    return decorator

# --------------------------------------------------------
def verificar_usuario(f):
    """
    Vamos receber uma função como argumento (a endpoint)
    e depois retornar uma função nova.
    Isso é um decorator
    """

    @wraps(f) # Preservando metadados para não causar overwrite nas funções
    def decorator(*args, **kwargs):         # *args, **kwargs repassam os parâmetros (aqui é 'usuario_id')
        usuario_id = kwargs.get("usuario_id") # Recebendo o valor de usuario_id que veio da endpoint
        usuario = bd.usuarios.get(usuario_id)
        if not usuario:
            return jsonify({"Erro": "Usuário não encontrado"}), 404
        kwargs["usuario"] = usuario
        return f(*args, **kwargs) # Caso exista, vamos repassar para a endpoint
    return decorator # Por fim embrulhamos a função bem pimposa pro Flask

def verificar_livro(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        livro_id = kwargs.get("livro_id")
        livro = bd.livros.get(livro_id)
        if not livro:
            return jsonify({"Erro": "Livro não encontrado"}), 404
        kwargs["livro"] = livro
        return f(*args, **kwargs)
    return decorator

############################################
        ########## LIVROS ##########
            ####################
# POST de livros
@livrosRoute.route("/", methods=['post'])

def uparLivro():
    if request.is_json: # Verifica se o conteúdo é JSON ou form data, onde sera mandado o json para p banco e o form para o html
        data = request.get_json()
    else:
        data = request.form

    novo_livro = bd.cadastrarLivro(
        str(uuid.uuid4()),
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"]
    )
    return jsonify(novo_livro.__dict__), 201


# GET de livro com ID
@livrosRoute.route("/<livro_id>", methods=['get'])
@verificar_livro
def retornarLivroId(livro_id):
    livro = bd.livros.get(livro_id)
    return jsonify(livro.__dict__), 200

# GET de todos os livros
@livrosRoute.route("/", methods=['get'])
def retornarLivros():
    return jsonify([livro.__dict__ for livro in bd.livros.values()]), 200

# Cadastro de livros
@livrosRoute.route("/cadastro", methods=['post'])
def cadastrarLivro():
    data = request.form
    imagem_url = data.get("imagem")  # aqui pegamos a URL

    novo_livro = bd.cadastrarLivro(
        str(uuid.uuid4()),
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"],
        imagem_url
    )

    return jsonify(novo_livro.__dict__), 201

# PUT de livro
@livrosRoute.route("/<livro_id>", methods= ['put'])
@verificar_livro
def editarLivro(livro_id):
    livro_existe = bd.livros.get(livro_id)
    if not livro_existe:
        return jsonify({"Erro": "Livro não encontrado"}), 404

    data = request.get_json()

    livroEditado = bd.editarLivro(
        livro_id,
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"]
    )

    return jsonify(livroEditado.__dict__), 200

############################################
        ########## USUARIOS ##########
            ####################

# POST de cadastro de usuario e processa os dados
@usuariosRoute.route("/cadastro", methods=['post'])
def cadastrarUsuario():
    if request.is_json: # Verifica se o conteúdo é JSON ou form data, onde sera mandado o json para p banco e o form para o html
        data = request.get_json()
    else:
        data = request.form

    novo_usuario = bd.cadastrarUsuario(
        str(uuid.uuid4()),
        data["nome"],
        data["email"],
        data["senha"],
        data["data_nasc"]
    )

    if novo_usuario is None:
        # Já existe um usuário com esse e-mail
        return jsonify({"erro": "E-mail já cadastrado!"}), 400

    return jsonify(novo_usuario.to_dict()), 201


# POST de login com autenticação JWT
@usuariosRoute.route("/login", methods=['POST'])
def login():
    if request.is_json:
        data = request.get_json() #Aceita tanto json quando form data
    else:
        data = request.form

    email = data.get("email")
    senha = data.get("senha")

    usuario = bd.buscarEmail(email)
    if usuario and usuario.verificar_senha(senha):
        token = gerar_token(usuario.id)

        return jsonify({
            "token": token,
            "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
            }
        }), 200

    return jsonify({"erro": "Email ou senha incorretos"}), 401

# GET de usuario com ID
@usuariosRoute.route("/<usuario_id>", methods=['get'])
@verificar_usuario
def retornarUsuarioId(usuario_id):
    usuario = bd.usuarios.get(usuario_id)
    return jsonify(usuario.to_dict()), 200

# GET de todos os usuarios
@usuariosRoute.route("/", methods=['get'])
def retornarUsuario():
    return jsonify([usuario.to_dict() for usuario in bd.usuarios.values()]), 200

############################################
        ########## LEITURAS ##########
            ####################

# @app.route("/leituras", methods=['Post'])
# @requerir_token
# def registrarLeitura():
@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=['post'])
@verificar_usuario
@verificar_livro
def registrarLeitura(usuario_id, livro_id):
    usuarioExiste = bd.usuarios.get(usuario_id)
    livroExiste = bd.livros.get(livro_id)
    if not usuarioExiste:
        return jsonify({"Erro": "Usuário não encontrado"}), 404
    if not livroExiste:
        return jsonify({"Erro": "Livro não encontrado"}), 404

    data = request.get_json()
    # data = request.form # EVENTUALMENTE, SUBSTITUIR O DE CIMA POR ESSE

    leitura = bd.cadastrarLeitura(
        usuario_id,
        livro_id,
        data["status"],
        data.get("avaliacao"),  # Esses aqui levam .get pois não são parâmetros obrigatórios
        data.get("data_leitura"),
        data.get("comentario")
    )

    return jsonify(leitura.__dict__), 201
    # return redirect(url_for("registro_leituras")) # EVENTUALMENTE, SUBSTITUIR O DE CIMA POR ESSE

# @app.route("/leituras", methods=['Get'])
# @requerir_token
# def carregarLeiturasUsuario():
@leiturasRoute.route("/<usuario_id>", methods=['get'])
@requerir_token
@verificar_usuario
def carregarLeiturasUsuario(id_usuario, usuario_id):
    leituras = bd.carregarLeituras(usuario_id)

    if not leituras:
        return jsonify({"Erro": "Nenhuma leitura encontrada para este usuário"}), 404

    return jsonify([leitura.__dict__ for leitura in leituras]), 200

# @app.route("/leituras", methods=['Put'])
# @requerir_token
# def registrarLeitura():]
@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=['put'])
@verificar_usuario
@verificar_livro
def editarLeitura(usuario_id, livro_id):

    leituras = bd.carregarLeituras(usuario_id)
    verificarLeitura = next((l for l in leituras if l.id_livro == livro_id), None)

    if not verificarLeitura:
        return jsonify({"erro": "Leitura não encontrada"}), 404

    data = request.get_json()
    # data = request.form # EVENTUALMENTE, SUBSTITUIR O DE CIMA POR ESSE

    leituraEditada = bd.editarLeitura(
        usuario_id,
        livro_id,
        data["status"],
        data.get("avaliacao"),  # Esses aqui levam .get pois não são parâmetros obrigatórios
        data.get("data_leitura"),
        data.get("comentario")
    )

    return jsonify(leituraEditada.__dict__), 201
    # return redirect(url_for("registro_leituras")) # EVENTUALMENTE, SUBSTITUIR O DE CIMA POR ESSE

############################################'''