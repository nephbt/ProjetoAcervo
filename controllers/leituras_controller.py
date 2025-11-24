from flask import Blueprint, jsonify, request
from database import bd
from controllers.auth_utils import verificar_usuario, verificar_livro, requerir_token
import uuid

leiturasRoute = Blueprint("leituras", __name__, url_prefix="/leituras")


@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=['POST'])
@requerir_token
@verificar_usuario
@verificar_livro
def registrarLeitura(id_usuario, usuario_id, livro_id, usuario, livro):
    """
    Registra uma nova leitura para o usuário.
    Requer autenticação via token JWT.
    """
    data = request.get_json()

    status = data.get("status")
    data_leitura = data.get("data_leitura")
    avaliacao = data.get("avaliacao")
    comentario = data.get("comentario")

    if not status or not data_leitura:
        return jsonify({"erro": "Campos obrigatórios faltando (status e data_leitura)"}), 400

    # Verificar se o id_usuario do token bate com o da URL
    if id_usuario != usuario_id:
        return jsonify({"erro": "Usuário não autorizado"}), 403

    # Cadastrar a leitura usando os IDs
    leitura = bd.cadastrarLeitura(
        usuario.id,
        livro.id,
        status,
        avaliacao,
        data_leitura,
        comentario
    )

    # Retorna JSON compatível
    return jsonify({
        "id_usuario": leitura.id_usuario,
        "id_livro": leitura.id_livro,
        "status": leitura.status,
        "avaliacao": leitura.avaliacao,
        "data_leitura": leitura.dataLeitura,
        "comentario": leitura.comentario
    }), 201


@leiturasRoute.route("/<usuario_id>", methods=['GET'])
@requerir_token
def carregarLeiturasUsuario(id_usuario, usuario_id):
    """
    Retorna todas as leituras de um usuário.
    Requer autenticação via token JWT.
    """
    # Verificar se o id_usuario do token bate com o da URL
    if id_usuario != usuario_id:
        return jsonify({"erro": "Usuário não autorizado"}), 403

    leituras = bd.carregarLeituras(usuario_id)

    if not leituras:
        # Retorna array vazio ao invés de erro 404
        return jsonify([]), 200

    # Converter objetos Leitura para dicionário
    leituras_dict = []
    for leitura in leituras:
        leituras_dict.append({
            "id_usuario": leitura.id_usuario,
            "id_livro": leitura.id_livro,
            "status": leitura.status,
            "avaliacao": leitura.avaliacao,
            "dataLeitura": leitura.dataLeitura,
            "data_leitura": leitura.dataLeitura,  # Alias para compatibilidade
            "comentario": leitura.comentario
        })

    return jsonify(leituras_dict), 200


@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=['PUT'])
@requerir_token
@verificar_usuario
@verificar_livro
def editarLeitura(id_usuario, usuario_id, livro_id, usuario, livro):
    """
    Edita uma leitura existente.
    Requer autenticação via token JWT.
    """
    # Verificar se o id_usuario do token bate com o da URL
    if id_usuario != usuario_id:
        return jsonify({"erro": "Usuário não autorizado"}), 403

    data = request.get_json()

    leituraEditada = bd.editarLeitura(
        usuario_id,
        livro_id,
        data["status"],
        data.get("avaliacao"),
        data.get("data_leitura"),
        data.get("comentario")
    )

    return jsonify({
        "id_usuario": leituraEditada.id_usuario,
        "id_livro": leituraEditada.id_livro,
        "status": leituraEditada.status,
        "avaliacao": leituraEditada.avaliacao,
        "data_leitura": leituraEditada.dataLeitura,
        "comentario": leituraEditada.comentario
    }), 200


@leiturasRoute.route("/todas", methods=['GET'])
def listarTodasLeituras():
    """
    Lista todas as leituras de todos os usuários.
    Endpoint público para fins administrativos/estatísticos.
    """
    todas_leituras = []

    # Percorre todos os usuários carregados no banco
    for usuario_id in bd.usuarios.keys():
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
        return jsonify([]), 200

    return jsonify(todas_leituras), 200