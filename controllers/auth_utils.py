from flask import jsonify, request
from functools import wraps
import jwt
import datetime
from database import BancoDados

bd = BancoDados()
key = "chave_bem_secreta"


def gerar_token(usuario_id):
    payload = {
        "id": usuario_id,
        "exp": datetime.datetime.now() + datetime.timedelta(hours=2),
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

        return f(id_usuario=id_usuario, *args, **kwargs)

    return decorator


def verificar_usuario(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        usuario_id = kwargs.get("usuario_id")
        usuario = bd.usuarios.get(usuario_id)
        if not usuario:
            return jsonify({"Erro": "Usuário não encontrado"}), 404
        # substitui usuario_id pelo objeto usuário
        return f(usuario=usuario, *args, **kwargs)

    return decorator


def verificar_livro(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        livro_id = kwargs.get("livro_id")
        livro = bd.livros.get(livro_id)

        # 🔍 Se não estiver no cache em memória, busca direto no banco
        if not livro:
            livro = bd.buscarLivroPorId(livro_id)

        if not livro:
            return jsonify({"Erro": "Livro não encontrado"}), 404

        # passa o objeto livro adiante para a rota
        return f(livro=livro, *args, **kwargs)

    return decorator
