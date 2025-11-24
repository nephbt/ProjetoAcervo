from flask import Blueprint, jsonify
from database import bd
from controllers.auth_utils import requerir_token, verificar_usuario
from controllers.recommendation_knn import recomendar_livros_knn

recommendationRoute = Blueprint("recomendacoes", __name__, url_prefix="/recomendacoes")


@recommendationRoute.route("/<usuario_id>", methods=['GET'])
@requerir_token
@verificar_usuario
def obter_recomendacoes(id_usuario, usuario_id, usuario):
    """
    Endpoint para obter recomendações personalizadas para um usuário.

    Uso: GET /recomendacoes/<usuario_id>
    Header: Authorization: Bearer <token>

    Retorna: Lista de livros recomendados com detalhes
    """
    try:
        # Obter IDs dos livros recomendados
        livros_recomendados_ids = recomendar_livros_knn(usuario_id, bd, num_recomendacoes=6)

        # Buscar detalhes dos livros
        livros_detalhados = []
        for livro_id in livros_recomendados_ids:
            livro = bd.buscarLivroPorId(livro_id)
            if livro:
                livros_detalhados.append({
                    "id": livro.id,
                    "titulo": livro.titulo,
                    "autor": livro.autor,
                    "genero": livro.genero,
                    "ano_publicacao": livro.ano_publicacao,
                    "imagem_url": livro.imagem_url
                })

        if not livros_detalhados:
            return jsonify({
                "mensagem": "Ainda não temos recomendações. Avalie alguns livros primeiro!",
                "recomendacoes": []
            }), 200

        return jsonify({
            "mensagem": "Recomendações baseadas no seu perfil de leitura",
            "recomendacoes": livros_detalhados
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao gerar recomendações: {str(e)}"}), 500