from flask import Blueprint, jsonify, request
from dbpostgres import bd
from controllers.auth_utils import verificar_usuario, verificar_livro, requerir_token

leiturasRoute = Blueprint("leituras", __name__, url_prefix="/leituras")


# ------------------------------------------------
# POST /leituras/<usuario_id>/<livro_id>
# ------------------------------------------------
@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=["POST"])
@verificar_usuario
@verificar_livro
def registrarLeitura(usuario_id, livro_id, usuario, livro):
    data = request.get_json()

    status = data.get("status")
    data_leitura = data.get("data_leitura")
    avaliacao = data.get("avaliacao")
    comentario = data.get("comentario")

    if not status or not data_leitura:
        return jsonify({"erro": "Campos obrigatórios faltando"}), 400

    leitura = bd.cadastrarLeitura(
        usuario.id,
        livro.id,
        status,
        avaliacao,
        data_leitura,
        comentario,
    )

    return jsonify({
        "id_usuario": leitura.id_usuario,
        "id_livro": leitura.id_livro,
        "status": leitura.status,
        "avaliacao": leitura.avaliacao,
        "data_leitura": leitura.dataLeitura,
        "comentario": leitura.comentario,
    }), 201


# ------------------------------------------------
# GET /leituras/<usuario_id>
# ------------------------------------------------
@leiturasRoute.route("/<usuario_id>", methods=["GET"])
@requerir_token
@verificar_usuario
def carregarLeiturasUsuario(usuario_id, usuario):
    leituras = bd.carregarLeituras(usuario_id)

    if not leituras:
        return jsonify({"Erro": "Nenhuma leitura encontrada"}), 404

    return jsonify([l.__dict__ for l in leituras]), 200


# ------------------------------------------------
# PUT /leituras/<usuario_id>/<livro_id>
# ------------------------------------------------
@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=["PUT"])
@verificar_usuario
@verificar_livro
def editarLeitura(usuario_id, livro_id, usuario, livro):
    data = request.get_json()

    leituraEditada = bd.editarLeitura(
        usuario_id,
        livro_id,
        data.get("status"),
        data.get("avaliacao"),
        data.get("data_leitura"),
        data.get("comentario"),
    )

    return jsonify(leituraEditada.__dict__), 201


# ------------------------------------------------
# GET /leituras/todas
# ------------------------------------------------
@leiturasRoute.route("/todas", methods=["GET"])
def listarTodasLeituras():
    # Agora buscamos todas diretamente no Postgres
    todas_leituras = bd.carregarTodasLeituras()

    if not todas_leituras:
        return jsonify({"mensagem": "Nenhuma leitura encontrada"}), 404

    return jsonify([
        {
            "id_usuario": leitura.id_usuario,
            "id_livro": leitura.id_livro,
            "status": leitura.status,
            "avaliacao": leitura.avaliacao,
            "data_leitura": leitura.dataLeitura,
            "comentario": leitura.comentario,
        }
        for leitura in todas_leituras
    ]), 200
