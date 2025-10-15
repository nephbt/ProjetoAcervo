from flask import Flask, request, jsonify, redirect, url_for, session
import uuid
import jwt
import datetime
from database import BancoDados

app = Flask(__name__)
bd = BancoDados()
SECRET_KEY = "chave_bem_secreta"

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

    novo_livro = bd.adicionarLivro(
        str(uuid.uuid4()),
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"]
    )
    return jsonify(novo_livro.__dict__), 201

# GET de livro com ID
@app.route("/livros/<livro_id>", methods=['Get'])
def retornarLivroId(livro_id):
    livro = bd.livros.get(livro_id)
    if livro:
        return jsonify(livro.__dict__), 200
    return jsonify({"Erro": "Livro não encontrado"}), 404

# GET de todos os livros
@app.route("/livros", methods=['Get'])
def retornarLivros():
    return jsonify([livro.__dict__ for livro in bd.livros.values()]), 200

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
def retornarUsuarioId(usuario_id):
    usuario = bd.usuarios.get(usuario_id)
    if usuario:
        return jsonify(usuario.to_dict()), 200
    return ({"Erro": "Usuário não encontrado"}), 404

# GET de todos os usuarios
@app.route("/usuarios", methods=['Get'])
def retornarUsuario():
    return jsonify([usuario.to_dict() for usuario in bd.usuarios.values()]), 200

############################################
def gerar_token(usuario_id):
    """
    Vamos gerar um JWT para o usuário, válido por 2 horas. :)
    """
    payload = {
        "id": usuario_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

if __name__ == '__main__':
    app.run(debug=True)