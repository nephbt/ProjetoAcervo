from flask import Blueprint, jsonify, request
from database import bd
import uuid
from controllers.auth_utils import verificar_livro

livrosRoute = Blueprint("livros", __name__, url_prefix="/livros")

@livrosRoute.route("/", methods=['post'])
def uparLivro():
    data = request.get_json() if request.is_json else request.form
    novo_livro = bd.cadastrarLivro(
        str(uuid.uuid4()),
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"]
    )
    return jsonify(novo_livro.__dict__), 201

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

@livrosRoute.route("/<livro_id>", methods=['get'])
@verificar_livro
def retornarLivroId(livro_id):
    livro = bd.livros.get(livro_id)
    return jsonify(livro.__dict__), 200

@livrosRoute.route("/", methods=['get'])
def retornarLivros():
    return jsonify([livro.__dict__ for livro in bd.livros.values()]), 200

@livrosRoute.route("/<livro_id>", methods=['put'])
@verificar_livro
def editarLivro(livro_id):
    data = request.get_json()
    livroEditado = bd.editarLivro(
        livro_id,
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"]
    )
    return jsonify(livroEditado.__dict__), 200