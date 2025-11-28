from flask import Blueprint, jsonify, request
from dbpostgres import bd
import uuid
from controllers.auth_utils import verificar_livro

livrosRoute = Blueprint("livros", __name__, url_prefix="/livros")


# -------------------------------------
# POST /livros/  → uparLivro
# -------------------------------------
@livrosRoute.route("/", methods=["POST"])
def uparLivro():
    data = request.get_json() if request.is_json else request.form

    novo_livro = bd.cadastrarLivro(
        str(uuid.uuid4()),
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"],
        data.get("imagem")  # opcional
    )

    return jsonify(novo_livro.__dict__), 201


# -------------------------------------
# POST /livros/cadastro → cadastrarLivro
# -------------------------------------
@livrosRoute.route("/cadastro", methods=["POST"])
def cadastrarLivro():
    data = request.form
    imagem_url = data.get("imagem")
    id = str(uuid.uuid4())  # ID único gerado pelo backend

    novo_livro = bd.cadastrarLivro(
        id,
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"],
        imagem_url,
    )

    return jsonify(novo_livro.__dict__), 201


# -------------------------------------
# GET /livros/<id> → retornarLivroId
# -------------------------------------
@livrosRoute.route("/<livro_id>", methods=["GET"])
@verificar_livro
def retornarLivroId(livro_id, livro):
    return jsonify(livro.__dict__), 200


# -------------------------------------
# GET /livros/ → retornarLivros
# -------------------------------------
@livrosRoute.route("/", methods=["GET"])
def retornarLivros():
    livros = bd.buscarTodosLivros()
    return jsonify([livro.__dict__ for livro in livros]), 200


# -------------------------------------
# PUT /livros/<id> → editarLivro
# -------------------------------------
@livrosRoute.route("/<livro_id>", methods=["PUT"])
def editarLivro(livro_id):
    dados = request.get_json()

    livro_existente = bd.buscarLivroPorId(livro_id)
    if not livro_existente:
        return jsonify({"erro": "Livro não encontrado"}), 404

    livro_atualizado = bd.editarLivro(
        livro_id,
        dados.get("titulo"),
        dados.get("autor"),
        dados.get("genero"),
        dados.get("ano_publicacao"),
        dados.get("imagem_url")
    )

    return jsonify({
        "mensagem": "Livro atualizado com sucesso!",
        "livro": livro_atualizado.__dict__
    }), 200


# -------------------------------------
# DELETE /livros/<id> → excluirLivro
# -------------------------------------
@livrosRoute.route("/<livro_id>", methods=["DELETE"])
@verificar_livro
def excluirLivro(livro_id, livro):
    sucesso = bd.excluirLivro(livro_id)

    if not sucesso:
        return jsonify({"erro": "Erro ao excluir o livro"}), 500

    return jsonify({
        "mensagem": f"Livro '{livro.titulo}' excluído com sucesso!"
    }), 200
