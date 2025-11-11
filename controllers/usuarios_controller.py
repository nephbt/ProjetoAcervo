from flask import Blueprint, jsonify, render_template, request, session
from database import bd
from controllers.auth_utils import gerar_token, requerir_token, verificar_usuario
import uuid

usuariosRoute = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@usuariosRoute.route("/cadastro", methods=['post'])
def cadastrarUsuario():
    data = request.get_json() if request.is_json else request.form
    novo_usuario = bd.cadastrarUsuario(
        str(uuid.uuid4()),
        data["nome"],
        data["email"],
        data["senha"],
        data["data_nasc"]
    )

    if novo_usuario is None:
        return jsonify({"erro": "E-mail já cadastrado!"}), 400

    return jsonify(novo_usuario.to_dict()), 201

@usuariosRoute.route("/login", methods=['POST'])
def login():
    data = request.get_json() if request.is_json else request.form
    usuario = bd.buscarEmail(data.get("email"))
    if usuario and usuario.verificar_senha(data.get("senha")):
        session["usuario_id"] = usuario.id  # Armazena o ID do usuário na sessão
        
        token = gerar_token(usuario.id)
        return jsonify({
            "token": token,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email
            }
        }), 200
    return jsonify({"erro": "Email ou senha incorretos"}), 401

@usuariosRoute.route("/<usuario_id>", methods=['get'])
@verificar_usuario
def retornarUsuarioId(usuario_id):
    usuario = bd.usuarios.get(usuario_id)
    return jsonify(usuario.to_dict()), 200

@usuariosRoute.route("/", methods=['get'])
def retornarUsuario():
    return jsonify([usuario.to_dict() for usuario in bd.usuarios.values()]), 200

@usuariosRoute.route("/perfil", methods=["GET"])
@requerir_token
def perfil(id_usuario):
    return jsonify({"mensagem": f"Bem-vindo usuário {id_usuario}!"}), 200


