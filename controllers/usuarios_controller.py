from flask import Blueprint, jsonify, request, session, render_template
from dbpostgres import bd, get_connection
from controllers.auth_utils import gerar_token, requerir_token, requerir_admin, verificar_usuario
import uuid

usuariosRoute = Blueprint("usuarios", __name__, url_prefix="/usuarios")


# ============================================================
# ROTAS PÚBLICAS
# ============================================================

@usuariosRoute.route("/perfil-page")
@requerir_token
def perfil_page(usuario_id, usuario_role, **kwargs):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, nome, email, data_nasc, role 
                FROM usuarios WHERE id = %s
            """, (usuario_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()

    if not row:
        return "Usuário não encontrado", 404

    usuario = {
        "id": row[0],
        "nome": row[1],
        "email": row[2],
        "data_nasc": row[3],
        "role": row[4]
    }

    return render_template("perfil.html", usuario=usuario)


@usuariosRoute.route("/cadastro", methods=["POST"])
def cadastrarUsuario():
    """Cadastra um novo usuário."""
    data = request.get_json() if request.is_json else request.form.to_dict()

    campos_obrigatorios = ["nome", "email", "senha", "data_nasc"]
    campos_faltando = [c for c in campos_obrigatorios if not data.get(c)]

    if campos_faltando:
        return jsonify({
            "erro": "Campos obrigatórios faltando",
            "campos": campos_faltando
        }), 400

    email = data.get("email", "").strip().lower()

    if "@" not in email or "." not in email:
        return jsonify({"erro": "Email inválido"}), 400

    try:
        novo_usuario = bd.cadastrarUsuario(
            id=str(uuid.uuid4()),
            nome=data["nome"].strip(),
            email=email,
            senha=data["senha"],
            data_nasc=data["data_nasc"],
            role="usuario"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

    if not novo_usuario:
        return jsonify({"erro": "E-mail já cadastrado!"}), 400

    return jsonify(novo_usuario.to_dict()), 201


@usuariosRoute.route("/login", methods=["POST"])
def login():
    """Autentica usuário e retorna token JWT."""
    data = request.get_json() if request.is_json else request.form.to_dict()

    email = data.get("email", "").strip().lower()
    senha = data.get("senha", "")

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    usuario = bd.buscarEmail(email)

    if not usuario:
        return jsonify({"erro": "Email ou senha incorretos"}), 401

    if not usuario.verificar_senha(senha):
        return jsonify({"erro": "Email ou senha incorretos"}), 401

    session["usuario_id"] = usuario.id
    token = gerar_token(usuario.id, usuario.role)

    return jsonify({
        "token": token,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "role": usuario.role
        }
    }), 200


@usuariosRoute.route("/logout", methods=["POST"])
def logout():
    """Encerra a sessão."""
    session.pop("usuario_id", None)
    return jsonify({"mensagem": "Logout realizado com sucesso"}), 200


# ============================================================
# ROTAS DE USUÁRIO AUTENTICADO
# ============================================================

@usuariosRoute.route("/perfil", methods=["GET"])
@requerir_token
def perfil(usuario_id, usuario_role, **kwargs):
    """Retorna o perfil do usuário autenticado."""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, nome, email, data_nasc, role 
                FROM usuarios WHERE id = %s
            """, (usuario_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()

    if not row:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    return jsonify({
        "id": row[0],
        "nome": row[1],
        "email": row[2],
        "data_nasc": str(row[3]) if row[3] else None,
        "role": row[4]
    }), 200


@usuariosRoute.route("/<usuario_id>", methods=["GET"])
@verificar_usuario
def retornarUsuarioId(usuario_id, usuario):
    """Retorna os dados de um usuário específico."""
    usuario_seguro = {k: v for k, v in usuario.items() if k != "senha"}
    return jsonify(usuario_seguro), 200


@usuariosRoute.route("/", methods=["GET"])
def retornarUsuarios():
    """Retorna todos os usuários cadastrados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, nome, email, data_nasc, role FROM usuarios")
            rows = cursor.fetchall()
        finally:
            cursor.close()

    usuarios = [
        {
            "id": row[0],
            "nome": row[1],
            "email": row[2],
            "data_nasc": str(row[3]) if row[3] else None,
            "role": row[4]
        }
        for row in rows
    ]

    return jsonify(usuarios), 200


# ============================================================
# ROTAS DE ADMIN
# ============================================================

@usuariosRoute.route("/admin/tornar-admin/<usuario_id>", methods=["POST"])
@requerir_admin
def tornarAdmin(admin_id, usuario_id):
    """Promove um usuário a administrador."""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT role, nome FROM usuarios WHERE id = %s",
                (usuario_id,)
            )
            row = cursor.fetchone()

            if not row:
                return jsonify({"erro": "Usuário não encontrado"}), 404

            if row[0] == "admin":
                return jsonify({"erro": "Usuário já é administrador"}), 400

            cursor.execute(
                "UPDATE usuarios SET role = 'admin' WHERE id = %s",
                (usuario_id,)
            )
            conn.commit()
            nome_usuario = row[1]

        finally:
            cursor.close()

    return jsonify({
        "mensagem": f"'{nome_usuario}' agora é administrador!",
        "usuario_id": usuario_id,
        "role": "admin"
    }), 200