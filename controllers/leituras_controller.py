from flask import Blueprint, jsonify, request
from dbpostgres import bd
from controllers.auth_utils import verificar_usuario, verificar_livro, requerir_token


leiturasRoute = Blueprint("leituras", __name__, url_prefix="/leituras")


# ------------------------------------------------
# POST /leituras/<usuario_id>/<livro_id>
# ------------------------------------------------
@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=["POST"])
def registrarLeitura(usuario_id, livro_id):
    
    data = request.get_json()

    status = data.get("status")
    data_leitura = data.get("data_leitura")
    avaliacao = data.get("avaliacao")
    comentario = data.get("comentario")

    if not status or not data_leitura:
        return jsonify({"erro": "Campos obrigatórios faltando"}), 400

    try:
        leitura = bd.cadastrarLeitura(
            idUsuario=usuario_id,
            idLivro=livro_id,
            status=status,
            avaliacao=avaliacao,
            dataLeitura=data_leitura,
            comentario=comentario
        )
    except Exception as e:
        import traceback
        print("Erro ao cadastrar leitura:")
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

    return jsonify(leitura.to_dict()), 201

# ------------------------------------------------
# GET /leituras/<usuario_id>
# ------------------------------------------------
@leiturasRoute.route("/<usuario_id>", methods=["GET"])
@requerir_token
@verificar_usuario
def carregarLeiturasUsuario(usuario_id, usuario):
    leituras = bd.carregarLeituras(usuario_id)

    if not leituras:
        return jsonify({"erro": "Nenhuma leitura encontrada"}), 404

    return jsonify([l.to_dict() for l in leituras]), 200


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

    if not leituraEditada:
        return jsonify({"erro": "Leitura não encontrada"}), 404

    return jsonify(leituraEditada.to_dict()), 200


# ------------------------------------------------
# GET /leituras/todas
# ------------------------------------------------
@leiturasRoute.route("/todas", methods=["GET"])
def listarTodasLeituras():
    todas_leituras = bd.carregarTodasLeituras()

    if not todas_leituras:
        return jsonify({"mensagem": "Nenhuma leitura encontrada"}), 404

    return jsonify([l.to_dict() for l in todas_leituras]), 200
