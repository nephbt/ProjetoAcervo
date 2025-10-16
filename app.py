from flask import Flask, request, jsonify, redirect, url_for, session
from functools import wraps
import uuid
import jwt
import datetime
from database import BancoDados

app = Flask(__name__)
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



@app.route("/")
def homepage():
    # Retornar index.html aqui
    return "oi sou um placeholder"

@app.route("/entrar")
def loginECadastro():
    # Retornar html da página de login/cadastro
    return "oi sou outro placeholder"

############################################
        ########## LIVROS ##########
            ####################

# POST de livros
@app.route("/livros", methods=['Post'])
def uparLivro():
    data = request.get_json()

    novo_livro = bd.cadastrarLivro(
        str(uuid.uuid4()),
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"]
    )
    return jsonify(novo_livro.__dict__), 201

# GET de livro com ID
@app.route("/livros/<livro_id>", methods=['Get'])
@verificar_livro
def retornarLivroId(livro_id):
    livro = bd.livros.get(livro_id)
    return jsonify(livro.__dict__), 200

# GET de todos os livros
@app.route("/livros", methods=['Get'])
def retornarLivros():
    return jsonify([livro.__dict__ for livro in bd.livros.values()]), 200

# PUT de livro
@app.route("/livros/<livro_id>", methods= ['Put'])
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

# POST de cadastro de usuario
@app.route("/usuarios/cadastro", methods=['Post'])
def cadastrarUsuario():
    data = request.get_json()
    # data = request.form # EVENTUALMENTE, SUBSTITUIR O DE CIMA POR ESSE

    cadastro = bd.cadastrarUsuario(
        str(uuid.uuid4()),
        data["nome"],
        data["email"],
        data["senha"],
        data["data_nasc"]
    )
    return jsonify(cadastro.to_dict()), 201

# POST de login com autenticação JWT
@app.route("/usuarios/login", methods=['Post'])
def login():
    data = request.get_json()
    # data = request.form # EVENTUALMENTE, SUBSTITUIR O DE CIMA POR ESSE
    email = data.get("email")
    senha = data.get("senha")

    usuario = bd.buscarEmail(email)
    if usuario and usuario.verificar_senha(senha):
        token = gerar_token(usuario.id)

        # session["token"] = token # Para eventualmente, quando houver formulario html de login

        return jsonify({"token": token, "usuario":{"id": usuario["id"], "nome": usuario["nome"], "email": usuario["email"]}})
        # return redirect(url_for("home_usuario")) # EVENTUALMENTE, SUBSTITUIR O DE CIMA POR ESSE

    return jsonify({"erro": "Email ou senha incorretos"}), 401

# GET de usuario com ID
@app.route("/usuarios/<usuario_id>", methods=['Get'])
@verificar_usuario
def retornarUsuarioId(usuario_id):
    usuario = bd.usuarios.get(usuario_id)
    return jsonify(usuario.to_dict()), 200

# GET de todos os usuarios
@app.route("/usuarios", methods=['Get'])
@verificar_usuario
def retornarUsuario():
    return jsonify([usuario.to_dict() for usuario in bd.usuarios.values()]), 200

############################################
        ########## LEITURAS ##########
            ####################

# @app.route("/leituras", methods=['Post'])
# @requerir_token
# def registrarLeitura():
@app.route("/leituras/<usuario_id>/<livro_id>", methods=['Post'])
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
@app.route("/leituras/<usuario_id>", methods=['Get'])
def carregarLeiturasUsuario(usuario_id):
    leituras = bd.carregarLeituras(usuario_id)

    if not leituras:
        return jsonify({"Erro": "Nenhuma leitura encontrada para este usuário"}), 404

    return jsonify([leitura.__dict__ for leitura in leituras]), 200

# @app.route("/leituras", methods=['Put'])
# @requerir_token
# def registrarLeitura():]
@verificar_usuario
@verificar_livro
@app.route("/leituras/<usuario_id>/<livro_id>", methods=['Put'])
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

############################################

if __name__ == '__main__':
    app.run(debug=True)