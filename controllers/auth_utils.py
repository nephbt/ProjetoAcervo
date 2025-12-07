from flask import jsonify, request
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone
import os

from dbpostgres import bd, get_connection

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "chave_bem_secreta")


# ----------------------------
# Gerar Token JWT
# ----------------------------
def gerar_token(usuario_id, role="usuario"):
    """Gera um token JWT válido por 2 horas."""
    payload = {
        "id": usuario_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# ----------------------------
# Decorator: Exigir Token
# ----------------------------
def requerir_token(f):
    """Verifica se o token JWT é válido e injeta nomes compatíveis."""
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"erro": "Token ausente"}), 401

        try:
            token = token.replace("Bearer ", "")
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            token_usuario_id = decoded["id"]
            token_role = decoded.get("role", "usuario")
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401

        # Injetar nomes compatíveis: (mantemos token_* e adicionamos usuario_*)
        kwargs["token_usuario_id"] = token_usuario_id
        kwargs["token_role"] = token_role

        # Nomes antigos usados nas rotas: usuario_id / usuario_role
        # Só sobrescreve se não existirem (evita clobbering)
        if "usuario_id" not in kwargs:
            kwargs["usuario_id"] = token_usuario_id
        if "usuario_role" not in kwargs:
            kwargs["usuario_role"] = token_role

        return f(*args, **kwargs)
    return decorator


def requerir_admin(f):
    """Verifica se o usuário é administrador."""
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"erro": "Token ausente"}), 401

        try:
            token = token.replace("Bearer ", "")
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            admin_id = decoded["id"]
            admin_role = decoded.get("role", "usuario")
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401

        if admin_role != "admin":
            return jsonify({"erro": "Acesso restrito a administradores"}), 403

        # SÓ admin_id - REMOVA as linhas usuario_id e usuario_role
        kwargs["admin_id"] = admin_id

        return f(*args, **kwargs)
    return decorator



# ----------------------------
# Decorator: Verificar Usuário
# ----------------------------
def verificar_usuario(f):
    """Busca o usuário no PostgreSQL e passa o objeto para a rota."""
    @wraps(f)
    def decorator(*args, **kwargs):
        usuario_id = kwargs.get("usuario_id")

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, nome, email, senha, data_nasc, role FROM usuarios WHERE id = %s",
                (usuario_id,)
            )
            row = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if not row:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        usuario = {
            "id": row[0],
            "nome": row[1],
            "email": row[2],
            "senha": row[3],
            "data_nasc": row[4],
            "role": row[5]
        }

        kwargs.pop("usuario_id", None)
        return f(usuario=usuario, *args, **kwargs)

    return decorator


# ----------------------------
# Decorator: Verificar Livro (apenas aprovados)
# ----------------------------
def verificar_livro(f):
    """Busca o livro aprovado no banco e passa para a rota."""
    @wraps(f)
    def decorator(*args, **kwargs):
        livro_id = kwargs.get("livro_id")

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, titulo, autor, genero, ano_publicacao, imagem_url, status_aprovacao
                FROM livros WHERE id = %s
            """, (livro_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if not row:
            return jsonify({"erro": "Livro não encontrado"}), 404

        livro = {
            "id": row[0],
            "titulo": row[1],
            "autor": row[2],
            "genero": row[3],
            "ano_publicacao": row[4],
            "imagem_url": row[5],
            "status_aprovacao": row[6]
        }

        kwargs.pop("livro_id", None)
        return f(livro=livro, *args, **kwargs)

    return decorator


# ----------------------------
# Decorator: Verificar Livro Aprovado (para leituras)
# ----------------------------
def verificar_livro_aprovado(f):
    """Busca o livro e verifica se está aprovado."""
    @wraps(f)
    def decorator(*args, **kwargs):
        livro_id = kwargs.get("livro_id")

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, titulo, autor, genero, ano_publicacao, imagem_url, status_aprovacao
                FROM livros WHERE id = %s
            """, (livro_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if not row:
            return jsonify({"erro": "Livro não encontrado"}), 404

        if row[6] != "aprovado":
            return jsonify({"erro": "Livro ainda não foi aprovado pelo administrador"}), 403

        livro = {
            "id": row[0],
            "titulo": row[1],
            "autor": row[2],
            "genero": row[3],
            "ano_publicacao": row[4],
            "imagem_url": row[5],
            "status_aprovacao": row[6]
        }

        kwargs.pop("livro_id", None)
        return f(livro=livro, *args, **kwargs)

    return decorator

def buscar_usuario_por_id(usuario_id):
    """Retorna dict do usuário ou None."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, nome, email, senha, data_nasc, role FROM usuarios WHERE id = %s",
            (usuario_id,)
        )
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "nome": row[1],
        "email": row[2],
        "senha": row[3],
        "data_nasc": row[4],
        "role": row[5],
    }


def buscar_livro_por_id(livro_id):
    """Retorna dict do livro (com imagem_url) ou None."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, titulo, autor, genero, ano_publicacao, imagem_url, status_aprovacao
            FROM livros WHERE id = %s
        """, (livro_id,))
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "titulo": row[1],
        "autor": row[2],
        "genero": row[3],
        "ano_publicacao": row[4],
        "imagem_url": row[5],
        "status_aprovacao": row[6]
    }