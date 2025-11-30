from flask import jsonify, request
from functools import wraps
import jwt
import datetime
from dbpostgres import bd
from dbpostgres import get_connection

key = "chave_bem_secreta"


def gerar_token(usuario_id):
    payload = {
        "id": usuario_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, key, algorithm="HS256")
    return token


def requerir_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"erro": "Token ausente"}), 401

        try:
            token = token.replace("Bearer ", "")
            decoded = jwt.decode(token, key, algorithms=["HS256"])
            id_usuario = decoded["id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401

        return f(usuario_id=id_usuario, *args, **kwargs)

    return decorator


# -----------------------------------------------------------------
# Consulta o PostgreSQL
# -----------------------------------------------------------------
def verificar_usuario(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        usuario_id = kwargs.get("usuario_id")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nome, email, senha, data_nasc FROM usuarios WHERE id = %s",
            (usuario_id,)
        )

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return jsonify({"Erro": "Usuário não encontrado"}), 404
        
        usuario = {
            "id": row[0],
            "nome": row[1],
            "email": row[2],
            "senha": row[3],
            "data_nasc": row[4]
        }

        return f(usuario=usuario, *args, **kwargs)

    return decorator


def verificar_livro(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        livro_id = kwargs.get("livro_id")

        livro = bd.buscarLivroPorId(livro_id)

        if not livro:
            return jsonify({"Erro": "Livro não encontrado"}), 404

        return f(livro=livro, *args, **kwargs)

    return decorator
