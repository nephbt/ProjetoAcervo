from flask import Blueprint, jsonify, request
from dbpostgres import get_connection
from controllers.auth_utils import requerir_token, buscar_livro_por_id
from estruturas.lista_encadeada import GerenciadorLeituras
from controllers.recomendacoes_controller import limpar_cache_usuario
from datetime import datetime
import uuid

leiturasRoute = Blueprint("leituras", __name__, url_prefix="/leituras")

# ============================================================
# LISTA ENCADEADA DE LEITURAS (Estrutura de Dados)
# ============================================================

gerenciador_leituras = GerenciadorLeituras()


def carregar_leituras_do_banco():
    """
    Carrega todas as leituras do banco para as listas encadeadas.
    """
    global gerenciador_leituras
    gerenciador_leituras = GerenciadorLeituras()

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT l.id, l.id_usuario, l.id_livro, l.status, l.avaliacao, 
                       l.data_leitura, l.comentario,
                       liv.titulo, liv.autor, liv.imagem_url
                FROM leituras l
                JOIN livros liv ON l.id_livro = liv.id
                ORDER BY l.id_usuario, l.data_leitura DESC
            """)

            for row in cursor.fetchall():
                leitura = {
                    "id": row[0],
                    "id_usuario": row[1],
                    "id_livro": row[2],
                    "status": row[3],
                    "avaliacao": row[4],
                    "data_leitura": str(row[5]) if row[5] else None,
                    "comentario": row[6],
                    "titulo_livro": row[7],
                    "autor_livro": row[8],
                    "imagem_url": row[9]
                }
                gerenciador_leituras.adicionar_leitura(row[1], leitura)

            print(f"📚 Leituras carregadas: {gerenciador_leituras.total_leituras()} de {gerenciador_leituras.total_usuarios()} usuário(s)")
        except Exception as e:
            print(f"⚠️ Erro ao carregar leituras: {e}")
        finally:
            cursor.close()


carregar_leituras_do_banco()


# ============================================================
# ROTAS
# ============================================================

@leiturasRoute.route("/<usuario_id>", methods=["GET"])
@requerir_token
def carregarLeiturasUsuario(usuario_id, token_usuario_id, token_role, **kwargs):
    """
    Retorna as leituras de um usuário usando a LISTA ENCADEADA.
    """
    if usuario_id != token_usuario_id and token_role != 'admin':
        return jsonify({"erro": "Sem permissão para ver leituras de outro usuário"}), 403

    lista = gerenciador_leituras.obter_lista(usuario_id)
    leituras = lista.listar()

    return jsonify(leituras), 200


@leiturasRoute.route("/<usuario_id>/estatisticas", methods=["GET"])
@requerir_token
def estatisticasUsuario(usuario_id, token_usuario_id, token_role, **kwargs):
    """
    Retorna estatísticas das leituras calculadas pela lista encadeada.
    """
    if usuario_id != token_usuario_id and token_role != 'admin':
        return jsonify({"erro": "Sem permissão"}), 403

    stats = gerenciador_leituras.estatisticas_usuario(usuario_id)

    return jsonify({
        "estrutura": "Lista Encadeada - Estatísticas O(n)",
        "estatisticas": stats
    }), 200


@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=["POST"])
@requerir_token
def registrarLeitura(usuario_id, livro_id, token_usuario_id, token_role, **kwargs):
    """
    Registra uma nova leitura (adiciona no INÍCIO da lista encadeada).
    """
    if usuario_id != token_usuario_id:
        return jsonify({"erro": "Não pode registrar leitura para outro usuário"}), 403

    livro = buscar_livro_por_id(livro_id)
    if not livro:
        return jsonify({"erro": "Livro não encontrado"}), 404

    if livro.get('status_aprovacao') != 'aprovado':
        return jsonify({"erro": "Livro ainda não foi aprovado"}), 403

    lista = gerenciador_leituras.obter_lista(usuario_id)
    if lista.contem(livro_id):
        return jsonify({"erro": "Você já registrou leitura para este livro"}), 409

    data = request.get_json() or {}
    leitura_id = str(uuid.uuid4())

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO leituras (id, id_usuario, id_livro, status, avaliacao, data_leitura, comentario)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, status, avaliacao, data_leitura, comentario
            """, (
                leitura_id,
                usuario_id,
                livro_id,
                data.get("status", "quero_ler"),
                data.get("avaliacao"),
                data.get("data_leitura") or datetime.now(),
                data.get("comentario")
            ))

            row = cursor.fetchone()
            conn.commit()

            leitura_dict = {
                "id": row[0],
                "id_usuario": usuario_id,
                "id_livro": livro_id,
                "status": row[1],
                "avaliacao": row[2],
                "data_leitura": str(row[3]) if row[3] else None,
                "comentario": row[4],
                "titulo_livro": livro['titulo'],
                "autor_livro": livro['autor'],
                "imagem_url": livro.get('imagem_url')
            }
            lista.adicionar_inicio(leitura_dict)

        except Exception as e:
            conn.rollback()
            import traceback
            traceback.print_exc()
            return jsonify({"erro": str(e)}), 500
        finally:
            cursor.close()

    limpar_cache_usuario(usuario_id)

    return jsonify({
        "mensagem": "Leitura registrada com sucesso!",
        "posicao_lista": 1,
        "total_leituras": lista.tamanho(),
        "leitura": leitura_dict
    }), 201


@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=["PUT"])
@requerir_token
def editarLeitura(usuario_id, livro_id, token_usuario_id, token_role, **kwargs):
    """
    Edita uma leitura existente.
    """
    if usuario_id != token_usuario_id:
        return jsonify({"erro": "Não pode editar leitura de outro usuário"}), 403

    lista = gerenciador_leituras.obter_lista(usuario_id)

    resultado = lista.buscar(livro_id)
    if not resultado:
        return jsonify({"erro": "Leitura não encontrada"}), 404

    data = request.get_json() or {}

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE leituras
                SET status = COALESCE(%s, status),
                    avaliacao = COALESCE(%s, avaliacao),
                    comentario = COALESCE(%s, comentario)
                WHERE id_usuario = %s AND id_livro = %s
                RETURNING id, status, avaliacao, comentario
            """, (
                data.get("status"),
                data.get("avaliacao"),
                data.get("comentario"),
                usuario_id,
                livro_id
            ))

            row = cursor.fetchone()
            conn.commit()

            lista.atualizar(livro_id, {
                "status": row[1],
                "avaliacao": row[2],
                "comentario": row[3]
            })

        except Exception as e:
            conn.rollback()
            return jsonify({"erro": str(e)}), 500
        finally:
            cursor.close()

    limpar_cache_usuario(usuario_id)

    return jsonify({
        "mensagem": "Leitura atualizada!",
        "leitura": lista.buscar(livro_id)['leitura']
    }), 200


@leiturasRoute.route("/<usuario_id>/<livro_id>", methods=["DELETE"])
@requerir_token
def removerLeitura(usuario_id, livro_id, token_usuario_id, token_role, **kwargs):
    """
    Remove uma leitura.
    """
    if usuario_id != token_usuario_id and token_role != 'admin':
        return jsonify({"erro": "Sem permissão para remover esta leitura"}), 403

    lista = gerenciador_leituras.obter_lista(usuario_id)

    if not lista.contem(livro_id):
        return jsonify({"erro": "Leitura não encontrada"}), 404

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM leituras WHERE id_usuario = %s AND id_livro = %s
            """, (usuario_id, livro_id))

            conn.commit()
            lista.remover(livro_id)

        except Exception as e:
            conn.rollback()
            return jsonify({"erro": str(e)}), 500
        finally:
            cursor.close()

    return jsonify({
        "mensagem": "Leitura removida com sucesso!",
        "total_restante": lista.tamanho()
    }), 200


@leiturasRoute.route("/<usuario_id>/filtrar/<status>", methods=["GET"])
@requerir_token
def filtrarPorStatus(usuario_id, status, token_usuario_id, token_role, **kwargs):
    """
    Filtra leituras por status usando a lista encadeada.
    """
    if usuario_id != token_usuario_id and token_role != 'admin':
        return jsonify({"erro": "Sem permissão"}), 403

    lista = gerenciador_leituras.obter_lista(usuario_id)
    leituras_filtradas = lista.filtrar_por_status(status)

    return jsonify({
        "estrutura": "Lista Encadeada - Filtro O(n)",
        "status_filtro": status,
        "total": len(leituras_filtradas),
        "leituras": leituras_filtradas
    }), 200


@leiturasRoute.route("/todas", methods=["GET"])
def listarTodasLeituras():
    """
    Lista todas as leituras de todos os usuários (público).
    """
    todas = []

    for usuario_id, lista in gerenciador_leituras.leituras_por_usuario.items():
        for leitura in lista:
            todas.append(leitura)

    return jsonify({
        "total_usuarios": gerenciador_leituras.total_usuarios(),
        "total_leituras": len(todas),
        "leituras": todas
    }), 200