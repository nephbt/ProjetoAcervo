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
@livrosRoute.route("/cadastro", methods=['POST'])
def cadastrarLivro():
    data = request.form
    imagem_url = data.get("imagem")  # nome do campo do formulário
    id = str(uuid.uuid4())           # ID único gerado pelo backend

    novo_livro = bd.cadastrarLivro(
        id,
        data["titulo"],
        data["autor"],
        data["genero"],
        data["ano_publicacao"],
        imagem_url
    )

    return jsonify(novo_livro.__dict__), 201


@livrosRoute.route("/<livro_id>", methods=['GET'])
@verificar_livro
def retornarLivroId(livro_id, livro):
    return jsonify(livro.__dict__), 200


@livrosRoute.route("/", methods=['get'])
def retornarLivros():
    return jsonify([livro.__dict__ for livro in bd.livros.values()]), 200

@livrosRoute.route("/<livro_id>", methods=["PUT"])
def editarLivro(livro_id):
    dados = request.get_json()
    titulo = dados.get("titulo")
    autor = dados.get("autor")
    genero = dados.get("genero")
    ano_publicacao = dados.get("ano_publicacao")
    imagem_url = dados.get("imagem_url")

    livro_existente = bd.buscarLivroPorId(livro_id)
    if not livro_existente:
        return jsonify({"erro": "Livro não encontrado"}), 404

    livro_atualizado = bd.editarLivro(
        livro_id, titulo, autor, genero, ano_publicacao, imagem_url
    )

    return jsonify({
        "mensagem": "Livro atualizado com sucesso!",
        "livro": livro_atualizado.__dict__
    }), 200


@livrosRoute.route("/<livro_id>", methods=['DELETE'])
@verificar_livro
def excluirLivro(livro_id, livro):
    import sqlite3
    conn = sqlite3.connect(bd.db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
    conn.commit()
    conn.close()

    if livro_id in bd.livros:
        del bd.livros[livro_id]

    return jsonify({"mensagem": f"Livro '{livro.titulo}' excluído com sucesso!"}), 200