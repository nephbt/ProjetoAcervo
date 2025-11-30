from flask import Blueprint, jsonify, request, session
from dbpostgres import bd
from controllers.auth_utils import gerar_token, requerir_token, verificar_usuario

usuariosRoute = Blueprint("usuarios", __name__, url_prefix="/usuarios")


# -----------------------------
# Cadastro de usuário
# -----------------------------
@usuariosRoute.route("/cadastro", methods=["POST"])
def cadastrarUsuario():
    data = request.get_json() if request.is_json else request.form

    # Chama o método do BancoDados (PostgreSQL)
    novo_usuario = bd.cadastrarUsuario(
        data.get("nome"),
        data.get("email"),
        data.get("senha"),
        data.get("data_nasc")
    )

    if not novo_usuario:
        return jsonify({"erro": "E-mail já cadastrado!"}), 400

    return jsonify(novo_usuario.to_dict()), 201


# -----------------------------
# Login de usuário
# -----------------------------
@usuariosRoute.route("/login", methods=["POST"])
def login():
    data = request.get_json() if request.is_json else request.form
    usuario = bd.buscarEmail(data.get("email"))

    if usuario and usuario.verificar_senha(data.get("senha")):
        session["usuario_id"] = usuario.id  # mantém sessão (opcional)
        token = gerar_token(usuario.id)

        return jsonify({
            "token": token,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
            }
        }), 200

    return jsonify({"erro": "Email ou senha incorretos"}), 401


# -----------------------------
# Retornar usuário por ID
# -----------------------------
@usuariosRoute.route("/<usuario_id>", methods=["GET"])
@verificar_usuario
def retornarUsuarioId(usuario_id, usuario):
    # 'usuario' vem do decorator verificar_usuario
    return jsonify(usuario), 200


# -----------------------------
# Listar todos os usuários
# -----------------------------
@usuariosRoute.route("/", methods=["GET"])
def retornarUsuarios():
    usuarios = [u.to_dict() for u in bd.usuarios.values()]
    return jsonify(usuarios), 200


# -----------------------------
# Perfil do usuário (JWT)
# -----------------------------
@usuariosRoute.route("/perfil", methods=["get"])
@requerir_token
def perfil(usuario_id):
    return jsonify({"mensagem": f"Bem-vindo usuário {usuario_id}!"}), 200

