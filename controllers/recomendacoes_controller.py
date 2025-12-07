from flask import Blueprint, jsonify
from controllers.auth_utils import requerir_token, buscar_usuario_por_id
from ia.db_adapter import bd_adapter
from ia.recommendation_knn import recomendar_livros_knn, recomendar_livros_populares

recomendacoesRoute = Blueprint("recomendacoes", __name__, url_prefix="/recomendacoes")


@recomendacoesRoute.route("/<usuario_id>", methods=['GET'])
@requerir_token
def obter_recomendacoes(usuario_id, token_usuario_id, token_role, **kwargs):
    """
    Endpoint para obter recomendações personalizadas para um usuário.

    Usa algoritmo KNN (K-Nearest Neighbors) baseado em:
    - Similaridade de gêneros
    - Similaridade de autores
    - Ano de publicação
    - Avaliações dos usuários

    Uso: GET /recomendacoes/<usuario_id>
    Header: Authorization: Bearer <token>

    Retorna: Lista de livros recomendados com detalhes
    """
    # Verificar se usuário existe
    usuario = buscar_usuario_por_id(usuario_id)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    try:
        # Invalidar cache para garantir dados atualizados
        bd_adapter.invalidar_cache()

        # Obter IDs dos livros recomendados usando KNN
        livros_recomendados_ids = recomendar_livros_knn(
            usuario_id,
            bd_adapter,
            num_recomendacoes=6
        )

        # Buscar detalhes dos livros
        livros_detalhados = []
        for livro_id in livros_recomendados_ids:
            livro = bd_adapter.buscarLivroPorId(livro_id)
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
                "mensagem": "Ainda não temos recomendações personalizadas. Avalie alguns livros primeiro!",
                "tipo": "sem_dados",
                "recomendacoes": []
            }), 200

        return jsonify({
            "mensagem": "Recomendações baseadas no seu perfil de leitura",
            "algoritmo": "KNN (K-Nearest Neighbors) - Item-Based Collaborative Filtering",
            "tipo": "personalizada",
            "total": len(livros_detalhados),
            "recomendacoes": livros_detalhados
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": f"Erro ao gerar recomendações: {str(e)}"}), 500


@recomendacoesRoute.route("/populares", methods=['GET'])
def obter_livros_populares():
    """
    Retorna os livros mais bem avaliados (fallback quando não há dados suficientes).

    Uso: GET /recomendacoes/populares
    """
    try:
        bd_adapter.invalidar_cache()

        livros_ids = recomendar_livros_populares(bd_adapter, num_recomendacoes=10)

        livros_detalhados = []
        for livro_id in livros_ids:
            livro = bd_adapter.buscarLivroPorId(livro_id)
            if livro:
                livros_detalhados.append({
                    "id": livro.id,
                    "titulo": livro.titulo,
                    "autor": livro.autor,
                    "genero": livro.genero,
                    "ano_publicacao": livro.ano_publicacao,
                    "imagem_url": livro.imagem_url
                })

        return jsonify({
            "mensagem": "Livros mais bem avaliados pela comunidade",
            "tipo": "populares",
            "total": len(livros_detalhados),
            "recomendacoes": livros_detalhados
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": f"Erro ao buscar populares: {str(e)}"}), 500


@recomendacoesRoute.route("/estatisticas", methods=['GET'])
def obter_estatisticas_ia():
    """
    Retorna estatísticas do sistema de IA para debug.

    Uso: GET /recomendacoes/estatisticas
    """
    try:
        stats = bd_adapter.obter_estatisticas()

        return jsonify({
            "sistema": "KNN Item-Based Collaborative Filtering",
            "estatisticas": stats,
            "requisitos": {
                "minimo_avaliacoes_usuario": 2,
                "descricao": "Usuário precisa avaliar pelo menos 2 livros para recomendações personalizadas"
            }
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500