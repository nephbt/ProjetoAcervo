from flask import Blueprint, jsonify, request, session
from dbpostgres import bd
from controllers.auth_utils import gerar_token, requerir_token, verificar_usuario

usuariosRoute = Blueprint("usuarios", __name__, url_prefix="/usuarios")


# -------------------------------------
# POST /usuarios/cadastro → cadastrarUsuario
# -------------------------------------
@usuariosRoute.route("/cadastro", methods=["POST"])
def cadastrarUsuario():
    data = request.get_json() if request.is_json else request.form

    novo_usuario = bd.cadastrarUsuario(
        data["nome"],
        data["email"],
        data["senha"],
        data["data_nasc"]
    )

    if novo_usuario is None:
        return jsonify({"erro": "E-mail já cadastrado!"}), 400

    return jsonify(novo_usuario.to_dict()), 201


# -------------------------------------
# POST /usuarios/login → login
# -------------------------------------
@usuariosRoute.route("/login", methods=["POST"])
def login():
    data = request.get_json() if request.is_json else request.form

    usuario = bd.buscarEmail(data.get("email"))

    if usuario and usuario.verificar_senha(data.get("senha")):

        session["usuario_id"] = usuario.id  # mantém compatibilidade

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


# -------------------------------------
# GET /usuarios/<id> → retornarUsuarioId
# -------------------------------------
@usuariosRoute.route("/<usuario_id>", methods=["GET"])
@verificar_usuario
def retornarUsuarioId(usuario_id, usuario):
    """Agora recebe o usuário do decorator e não usa mais bd.usuarios."""
    return jsonify(usuario.to_dict()), 200


# -------------------------------------
# GET /usuarios/ → retornarUsuario
# -------------------------------------
@usuariosRoute.route("/", methods=["GET"])
def retornarUsuario():
    usuarios = bd.buscarTodosUsuarios()
    return jsonify([u.to_dict() for u in usuarios]), 200


# -------------------------------------
# GET /usuarios/perfil → perfil
# -------------------------------------
@usuariosRoute.route("/perfil", methods=["GET"])
@requerir_token
def perfil(id_usuario):
    return jsonify({"mensagem": f"Bem-vindo usuário {id_usuario}!"}), 200
