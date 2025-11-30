from flask import Blueprint, jsonify, request
from dbpostgres import bd
import uuid
from controllers.auth_utils import verificar_livro

livrosRoute = Blueprint("livros", __name__, url_prefix="/livros")

# ------------------------------------------------------
# POST /livros/  → cadastrar livro
# ------------------------------------------------------
@livrosRoute.route("/", methods=["POST"])
def cadastrarLivro():
    data = request.get_json() if request.is_json else request.form

    campos_obrigatorios = ["titulo", "autor", "genero", "ano_publicacao"]
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({"erro": f"Campo obrigatório faltando: {campo}"}), 400

    novo_livro = bd.cadastrarLivro(
        str(uuid.uuid4()),
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"],
        data.get("imagem")  # opcional
    )

    return jsonify(novo_livro.to_dict()), 201


# ------------------------------------------------------
# GET /livros/<id>
# ------------------------------------------------------
@livrosRoute.route("/<livro_id>", methods=["GET"])
@verificar_livro
def retornarLivroId(livro_id, livro):
    return jsonify(livro.to_dict()), 200


# ------------------------------------------------------
# GET /livros/
# ------------------------------------------------------
@livrosRoute.route("/", methods=["GET"])
def retornarLivros():
    livros = bd.buscarTodosLivros()
    return jsonify([livro.to_dict() for livro in livros]), 200


# ------------------------------------------------------
# PUT /livros/<id>
# ------------------------------------------------------
@livrosRoute.route("/<livro_id>", methods=["PUT"])
@verificar_livro
def editarLivro(livro_id, livro):
    dados = request.get_json()

    livro_atualizado = bd.editarLivro(
        livro_id,
        dados.get("titulo"),
        dados.get("autor"),
        dados.get("genero"),
        dados.get("ano_publicacao"),
        dados.get("imagem")
    )

    return jsonify({
        "mensagem": "Livro atualizado com sucesso!",
        "livro": livro_atualizado.to_dict()
    }), 200


# ------------------------------------------------------
# DELETE /livros/<id>
# ------------------------------------------------------
@livrosRoute.route("/<livro_id>", methods=["DELETE"])
@verificar_livro
def excluirLivro(livro_id, livro):
    sucesso = bd.excluirLivro(livro_id)

    if not sucesso:
        return jsonify({"erro": "Erro ao excluir o livro"}), 500

    return jsonify({
        "mensagem": f"Livro '{livro.titulo}' excluído com sucesso!"
    }), 200
