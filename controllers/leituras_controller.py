from flask import Blueprint, jsonify, request
from database import bd
from controllers.auth_utils import verificar_usuario, verificar_livro, requerir_token
import uuid

leiturasRoute = Blueprint("leituras", __name__, url_prefix="/leituras")

@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=['POST'])
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
    
    # cadastrar a leitura usando os IDs
    leitura = bd.cadastrarLeitura(
        usuario.id,   # id do objeto injetado
        livro.id,     # id do objeto injetado
        status,
        avaliacao,
        data_leitura,
        comentario
    )

    # retorna JSON compatível
    return jsonify({
        "id_usuario": leitura.id_usuario,
        "id_livro": leitura.id_livro,
        "status": leitura.status,
        "avaliacao": leitura.avaliacao,
        "data_leitura": leitura.dataLeitura,
        "comentario": leitura.comentario
    }), 201


@leiturasRoute.route("/<usuario_id>", methods=['get'])
@requerir_token
@verificar_usuario
def carregarLeiturasUsuario(usuario_id, usuario):
    leituras = bd.carregarLeituras(usuario_id)
    if not leituras:
        return jsonify({"Erro": "Nenhuma leitura encontrada"}), 404
    return jsonify([leitura.__dict__ for leitura in leituras]), 200

@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=['put'])
@verificar_usuario
@verificar_livro
def editarLeitura(usuario_id, livro_id):
    data = request.get_json()
    leituraEditada = bd.editarLeitura(
        usuario_id,
        livro_id,
        data["status"],
        data.get("avaliacao"),
        data.get("data_leitura"),
        data.get("comentario")
    )
    return jsonify(leituraEditada.__dict__), 201

@leiturasRoute.route("/todas", methods=['GET'])
def listarTodasLeituras():
    todas_leituras = []

    # Percorre todos os usuários carregados no banco
    for usuario_id, usuario in bd.usuarios.items():
        # bd.carregarLeituras retorna uma lista de objetos Leitura ou None
        leituras_usuario = bd.carregarLeituras(usuario_id)
        if leituras_usuario:
            for leitura in leituras_usuario:
                todas_leituras.append({
                    "id_usuario": leitura.id_usuario,
                    "id_livro": leitura.id_livro,
                    "status": leitura.status,
                    "avaliacao": leitura.avaliacao,
                    "data_leitura": leitura.dataLeitura,
                    "comentario": leitura.comentario
                })

    if not todas_leituras:
        return jsonify({"mensagem": "Nenhuma leitura encontrada"}), 404

    return jsonify(todas_leituras), 200