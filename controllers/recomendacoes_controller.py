from flask import Blueprint, jsonify
from controllers.auth_utils import requerir_token, buscar_usuario_por_id
from ia.db_adapter import bd_adapter
from ia.recommendation_knn import recomendar_livros_knn, recomendar_livros_populares
from datetime import datetime

recomendacoesRoute = Blueprint("recomendacoes", __name__, url_prefix="/recomendacoes")

# ============================================================
# SISTEMA DE CACHE
# ============================================================

_cache_recomendacoes = {}
_cache_populares = None
_cache_populares_timestamp = None
CACHE_TIMEOUT = 300  # 5 minutos


def cache_valido(timestamp):
    """Verifica se o cache ainda é válido."""
    if timestamp is None:
        return False
    return (datetime.now() - timestamp).seconds < CACHE_TIMEOUT


def limpar_cache_usuario(usuario_id):
    """Limpa o cache de um usuário específico (chamar após nova avaliação)."""
    if usuario_id in _cache_recomendacoes:
        del _cache_recomendacoes[usuario_id]


def limpar_todo_cache():
    """Limpa todo o cache (chamar após aprovar novo livro)."""
    global _cache_recomendacoes, _cache_populares, _cache_populares_timestamp
    _cache_recomendacoes = {}
    _cache_populares = None
    _cache_populares_timestamp = None


# ============================================================
# ROTAS
# ============================================================

@recomendacoesRoute.route("/<usuario_id>", methods=['GET'])
@requerir_token
def obter_recomendacoes(usuario_id, token_usuario_id, token_role, **kwargs):
    """
    Endpoint para obter recomendações personalizadas para um usuário.
    Usa cache para melhorar performance.
    """
    global _cache_recomendacoes

    # Verificar se usuário existe
    usuario = buscar_usuario_por_id(usuario_id)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    try:
        # ✅ VERIFICA CACHE PRIMEIRO
        if usuario_id in _cache_recomendacoes:
            dados, timestamp = _cache_recomendacoes[usuario_id]
            if cache_valido(timestamp):
                print(f"📦 Cache hit para usuário {usuario_id[:8]}...")
                dados["fonte"] = "cache"
                return jsonify(dados), 200

        print(f"🔄 Calculando recomendações para {usuario_id[:8]}...")

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
            resultado = {
                "mensagem": "Ainda não temos recomendações personalizadas. Avalie alguns livros primeiro!",
                "tipo": "sem_dados",
                "recomendacoes": []
            }
            return jsonify(resultado), 200

        resultado = {
            "mensagem": "Recomendações baseadas no seu perfil de leitura",
            "algoritmo": "KNN (K-Nearest Neighbors) - Item-Based Collaborative Filtering",
            "tipo": "personalizada",
            "total": len(livros_detalhados),
            "recomendacoes": livros_detalhados,
            "fonte": "calculado"
        }

        # ✅ SALVA NO CACHE
        _cache_recomendacoes[usuario_id] = (resultado.copy(), datetime.now())
        print(f"💾 Cache salvo para usuário {usuario_id[:8]}...")

        return jsonify(resultado), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": f"Erro ao gerar recomendações: {str(e)}"}), 500


@recomendacoesRoute.route("/populares", methods=['GET'])
def obter_livros_populares():
    """
    Retorna os livros mais bem avaliados.
    Usa cache para melhorar performance.
    """
    global _cache_populares, _cache_populares_timestamp

    try:
        # ✅ VERIFICA CACHE
        if _cache_populares and cache_valido(_cache_populares_timestamp):
            print("📦 Cache hit para populares")
            _cache_populares["fonte"] = "cache"
            return jsonify(_cache_populares), 200

        print("🔄 Calculando livros populares...")

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

        resultado = {
            "mensagem": "Livros mais bem avaliados pela comunidade",
            "tipo": "populares",
            "total": len(livros_detalhados),
            "recomendacoes": livros_detalhados,
            "fonte": "calculado"
        }

        # ✅ SALVA NO CACHE
        _cache_populares = resultado.copy()
        _cache_populares_timestamp = datetime.now()
        print("💾 Cache de populares salvo")

        return jsonify(resultado), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": f"Erro ao buscar populares: {str(e)}"}), 500


@recomendacoesRoute.route("/limpar-cache", methods=['POST'])
@requerir_token
def limpar_cache(token_usuario_id, token_role, **kwargs):
    """
    Limpa o cache de recomendações.
    Útil após avaliar um novo livro.
    """
    limpar_cache_usuario(token_usuario_id)
    return jsonify({"mensagem": "Cache limpo com sucesso!"}), 200


@recomendacoesRoute.route("/estatisticas", methods=['GET'])
def obter_estatisticas_ia():
    """
    Retorna estatísticas do sistema de IA.
    """
    try:
        stats = bd_adapter.obter_estatisticas()

        return jsonify({
            "sistema": "KNN Item-Based Collaborative Filtering",
            "estatisticas": stats,
            "cache": {
                "usuarios_em_cache": len(_cache_recomendacoes),
                "timeout_segundos": CACHE_TIMEOUT
            },
            "requisitos": {
                "minimo_avaliacoes_usuario": 2,
                "descricao": "Usuário precisa avaliar pelo menos 2 livros para recomendações personalizadas"
            }
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500