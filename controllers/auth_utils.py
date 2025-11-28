from flask import jsonify, request
from functools import wraps
import jwt
import datetime
from dbpostgres import bd  # AGORA usa o Postgres
# bd é sua instância de DatabasePostgres()

key = "chave_bem_secreta"


# ----------------------------
# Gerar Token
# ----------------------------
def gerar_token(usuario_id):
    payload = {
        "id": usuario_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, key, algorithm="HS256")
    return token


# ----------------------------
# Exigir token nas rotas
# ----------------------------
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


# ----------------------------
# Verificar existência do usuário
# ----------------------------
def verificar_usuario(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        usuario_id = kwargs.get("usuario_id")
        usuario = bd.usuarios.get(usuario_id)

        if not usuario:
            return jsonify({"Erro": "Usuário não encontrado"}), 404

        return f(usuario=usuario, *args, **kwargs)

    return decorator


# ----------------------------
# Verificar existência do livro
# ----------------------------
def verificar_livro(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        livro_id = kwargs.get("livro_id")

        # Primeiro tenta cache (se existir)
        livro = bd.livros.get(livro_id) if hasattr(bd, "livros") else None

        # Se não estiver no cache, busca no Postgres
        if not livro:
            livro = bd.buscarLivroPorId(livro_id)

        if not livro:
            return jsonify({"Erro": "Livro não encontrado"}), 404

        return f(livro=livro, *args, **kwargs)

    return decorator
