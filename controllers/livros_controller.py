from flask import Blueprint, jsonify, request
from dbpostgres import bd, get_connection
from controllers.auth_utils import verificar_livro, requerir_token, requerir_admin
from estruturas.fila import FilaAprovacao  # ← NOVO IMPORT
from datetime import datetime
import uuid

livrosRoute = Blueprint("livros", __name__, url_prefix="/livros")

# ============================================================
# FILA DE APROVAÇÃO (Estrutura de Dados)
# ============================================================

# Instância global da fila
fila_aprovacao = FilaAprovacao()


def carregar_fila_do_banco():
    """
    Carrega livros pendentes do banco para a fila na inicialização.
    Garante que a fila reflita o estado atual do banco.
    """
    global fila_aprovacao
    fila_aprovacao = FilaAprovacao()  # Limpa a fila antes de recarregar

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, titulo, autor, genero, ano_publicacao, imagem_url, cadastrado_por
            FROM livros 
            WHERE status_aprovacao = 'pendente'
            ORDER BY id
        """)

        for row in cursor.fetchall():
            livro = {
                "id": row[0],
                "titulo": row[1],
                "autor": row[2],
                "genero": row[3],
                "ano_publicacao": row[4],
                "imagem_url": row[5],
                "cadastrado_por": row[6]
            }
            fila_aprovacao.enfileirar(livro)

        print(f"📚 Fila de aprovação carregada com {fila_aprovacao.tamanho()} livro(s) pendente(s)")
    except Exception as e:
        print(f"⚠️ Erro ao carregar fila: {e}")
    finally:
        cursor.close()
        conn.close()


# Carrega a fila na inicialização do módulo
carregar_fila_do_banco()


# ============================================================
# ROTAS PÚBLICAS
# ============================================================

@livrosRoute.route("/", methods=["GET"])
def retornarLivros():
    """
    Retorna todos os livros APROVADOS (catálogo público).
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, titulo, autor, genero, ano_publicacao, imagem_url
            FROM livros 
            WHERE status_aprovacao = 'aprovado'
            ORDER BY titulo
        """)
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    livros = [
        {
            "id": row[0],
            "titulo": row[1],
            "autor": row[2],
            "genero": row[3],
            "ano_publicacao": row[4],
            "imagem_url": row[5]
        }
        for row in rows
    ]

    return jsonify(livros), 200


@livrosRoute.route("/<livro_id>", methods=["GET"])
@verificar_livro
def retornarLivroId(livro, **kwargs):
    """Retorna os dados de um livro específico."""
    livro_publico = {k: v for k, v in livro.items() if k not in ["status_aprovacao"]}
    return jsonify(livro_publico), 200


@livrosRoute.route("/busca", methods=["GET"])
def buscarLivros():
    """
    Busca livros APROVADOS por título, autor ou gênero.
    Query param: ?q=termo
    """
    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify([]), 200

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, titulo, autor, genero, ano_publicacao, imagem_url
            FROM livros
            WHERE status_aprovacao = 'aprovado'
              AND (LOWER(titulo) LIKE %s
                   OR LOWER(autor) LIKE %s
                   OR LOWER(genero) LIKE %s)
            ORDER BY titulo
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))

        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    livros = [
        {
            "id": row[0],
            "titulo": row[1],
            "autor": row[2],
            "genero": row[3],
            "ano_publicacao": row[4],
            "imagem_url": row[5]
        }
        for row in rows
    ]

    return jsonify(livros), 200


# ============================================================
# ROTAS DE USUÁRIO AUTENTICADO
# ============================================================

@livrosRoute.route("/", methods=["POST"])
@requerir_token
def cadastrarLivro(usuario_id, usuario_role, **kwargs):
    """
    Cadastra um novo livro com status 'pendente'.
    O livro entra na FILA de aprovação (FIFO).
    """
    data = request.get_json() if request.is_json else request.form.to_dict()

    # Validação
    campos_obrigatorios = ["titulo", "autor", "genero", "ano_publicacao"]
    campos_faltando = [c for c in campos_obrigatorios if not data.get(c)]

    if campos_faltando:
        return jsonify({
            "erro": "Campos obrigatórios faltando",
            "campos": campos_faltando
        }), 400

    livro_id = str(uuid.uuid4())

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO livros (id, titulo, autor, genero, ano_publicacao, imagem_url, 
                                status_aprovacao, cadastrado_por)
            VALUES (%s, %s, %s, %s, %s, %s, 'pendente', %s)
            RETURNING id, titulo, autor, genero, ano_publicacao, imagem_url, status_aprovacao
        """, (
            livro_id,
            data["titulo"].strip(),
            data["autor"].strip(),
            data["genero"].strip(),
            data["ano_publicacao"],
            data.get("imagem_url"),
            usuario_id
        ))

        row = cursor.fetchone()
        conn.commit()

        # ✅ ADICIONA NA FILA DE APROVAÇÃO
        livro_dict = {
            "id": row[0],
            "titulo": row[1],
            "autor": row[2],
            "genero": row[3],
            "ano_publicacao": row[4],
            "imagem_url": row[5],
            "cadastrado_por": usuario_id
        }
        fila_aprovacao.enfileirar(livro_dict)

    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "mensagem": "Livro cadastrado! Aguardando aprovação do administrador.",
        "posicao_fila": fila_aprovacao.tamanho(),  # ← Mostra posição na fila
        "livro": {
            "id": row[0],
            "titulo": row[1],
            "autor": row[2],
            "genero": row[3],
            "ano_publicacao": row[4],
            "imagem_url": row[5],
            "status_aprovacao": row[6]
        }
    }), 201


@livrosRoute.route("/meus", methods=["GET"])
@requerir_token
def meusLivrosCadastrados(usuario_id, usuario_role, **kwargs):
    """
    Retorna os livros cadastrados pelo usuário logado (todos os status).
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, titulo, autor, genero, ano_publicacao, imagem_url, 
                   status_aprovacao, motivo_rejeicao
            FROM livros 
            WHERE cadastrado_por = %s
            ORDER BY status_aprovacao, titulo
        """, (usuario_id,))
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    livros = []
    for row in rows:
        livro = {
            "id": row[0],
            "titulo": row[1],
            "autor": row[2],
            "genero": row[3],
            "ano_publicacao": row[4],
            "imagem_url": row[5],
            "status_aprovacao": row[6],
            "motivo_rejeicao": row[7]
        }

        # Se pendente, mostra posição na fila
        if row[6] == 'pendente':
            posicao = fila_aprovacao.buscar_por_id(row[0])
            livro['posicao_fila'] = posicao['posicao'] if posicao else None

        livros.append(livro)

    return jsonify(livros), 200


# ============================================================
# ROTAS DE ADMINISTRADOR
# ============================================================

@livrosRoute.route("/admin/fila", methods=["GET"])
@requerir_admin
def verFilaAprovacao(admin_id, **kwargs):
    """
    Retorna a fila de aprovação com posições (Estrutura de Dados: FILA).
    O primeiro da fila é o próximo a ser avaliado (FIFO).
    """
    return jsonify({
        "estrutura": "Fila (FIFO - First In, First Out)",
        "total": fila_aprovacao.tamanho(),
        "proximo": fila_aprovacao.primeiro(),
        "fila": fila_aprovacao.listar()
    }), 200


@livrosRoute.route("/admin/aprovar-proximo", methods=["POST"])
@requerir_admin
def aprovarProximoFila(admin_id, **kwargs):
    """
    Aprova o PRÓXIMO livro da fila (FIFO).
    Remove do início da fila e aprova no banco.
    """
    if fila_aprovacao.esta_vazia():
        return jsonify({"mensagem": "Fila vazia! Nenhum livro pendente."}), 200

    # Pega e remove o próximo da fila
    livro = fila_aprovacao.desenfileirar()

    # Atualiza no banco
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE livros 
            SET status_aprovacao = 'aprovado',
                data_aprovacao = %s,
                aprovado_por = %s,
                motivo_rejeicao = NULL
            WHERE id = %s
        """, (datetime.now(), admin_id, livro['id']))

        conn.commit()
    except Exception as e:
        conn.rollback()
        # Se der erro, recoloca na fila
        fila_aprovacao.enfileirar(livro)
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "mensagem": f"Livro '{livro['titulo']}' aprovado com sucesso!",
        "livro": livro,
        "restantes_na_fila": fila_aprovacao.tamanho()
    }), 200


@livrosRoute.route("/admin/pendentes", methods=["GET"])
@requerir_admin
def listarLivrosPendentes(admin_id, **kwargs):
    """
    Lista todos os livros aguardando aprovação.
    Usa a FILA para mostrar a ordem de chegada.
    """
    # Usa a fila para manter a ordem FIFO
    livros_fila = fila_aprovacao.listar()

    # Busca dados adicionais do banco (nome do usuário)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT l.id, u.nome as usuario_nome, u.email as usuario_email
            FROM livros l
            LEFT JOIN usuarios u ON l.cadastrado_por = u.id
            WHERE l.status_aprovacao = 'pendente'
        """)

        usuarios_map = {}
        for row in cursor.fetchall():
            usuarios_map[row[0]] = {"usuario_nome": row[1], "usuario_email": row[2]}
    finally:
        cursor.close()
        conn.close()

    # Enriquece os dados da fila com info do usuário
    for livro in livros_fila:
        info_usuario = usuarios_map.get(livro['id'], {})
        livro['usuario_nome'] = info_usuario.get('usuario_nome')
        livro['usuario_email'] = info_usuario.get('usuario_email')

    return jsonify({
        "estrutura": "Fila (FIFO)",
        "total": len(livros_fila),
        "proximo_a_avaliar": livros_fila[0] if livros_fila else None,
        "pendentes": livros_fila
    }), 200


@livrosRoute.route("/admin/aprovar/<livro_id>", methods=["POST"])
@requerir_admin
def aprovarLivro(admin_id, livro_id, **kwargs):
    """
    Aprova um livro específico (pode não ser o próximo da fila).
    Remove da fila independente da posição.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT status_aprovacao, titulo FROM livros WHERE id = %s
        """, (livro_id,))

        row = cursor.fetchone()

        if not row:
            return jsonify({"erro": "Livro não encontrado"}), 404

        if row[0] != "pendente":
            return jsonify({
                "erro": f"Livro não está pendente (status atual: {row[0]})"
            }), 400

        cursor.execute("""
            UPDATE livros 
            SET status_aprovacao = 'aprovado',
                data_aprovacao = %s,
                aprovado_por = %s,
                motivo_rejeicao = NULL
            WHERE id = %s
        """, (datetime.now(), admin_id, livro_id))

        conn.commit()
        titulo = row[1]

        # ✅ REMOVE DA FILA
        fila_aprovacao.remover_por_id(livro_id)

    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "mensagem": f"Livro '{titulo}' aprovado com sucesso!",
        "livro_id": livro_id,
        "status_aprovacao": "aprovado",
        "restantes_na_fila": fila_aprovacao.tamanho()
    }), 200


@livrosRoute.route("/admin/rejeitar/<livro_id>", methods=["POST"])
@requerir_admin
def rejeitarLivro(admin_id, livro_id, **kwargs):
    """
    Rejeita um livro pendente.
    Remove da fila de aprovação.
    """
    data = request.get_json() or {}
    motivo = data.get("motivo", "Não especificado")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT status_aprovacao, titulo FROM livros WHERE id = %s
        """, (livro_id,))

        row = cursor.fetchone()

        if not row:
            return jsonify({"erro": "Livro não encontrado"}), 404

        if row[0] == "aprovado":
            return jsonify({
                "erro": "Não é possível rejeitar um livro já aprovado"
            }), 400

        cursor.execute("""
            UPDATE livros 
            SET status_aprovacao = 'rejeitado',
                data_aprovacao = %s,
                aprovado_por = %s,
                motivo_rejeicao = %s
            WHERE id = %s
        """, (datetime.now(), admin_id, motivo, livro_id))

        conn.commit()
        titulo = row[1]

        # ✅ REMOVE DA FILA
        fila_aprovacao.remover_por_id(livro_id)

    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "mensagem": f"Livro '{titulo}' foi rejeitado",
        "livro_id": livro_id,
        "status_aprovacao": "rejeitado",
        "motivo": motivo,
        "restantes_na_fila": fila_aprovacao.tamanho()
    }), 200


@livrosRoute.route("/admin/todos", methods=["GET"])
@requerir_admin
def listarTodosLivrosAdmin(admin_id, **kwargs):
    """
    Lista todos os livros do sistema com filtros.
    Query params: ?status=pendente|aprovado|rejeitado
    """
    status_filtro = request.args.get("status")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if status_filtro:
            cursor.execute("""
                SELECT l.id, l.titulo, l.autor, l.genero, l.ano_publicacao, l.imagem_url,
                       l.status_aprovacao, l.data_aprovacao, l.motivo_rejeicao,
                       u.nome as usuario_nome
                FROM livros l
                LEFT JOIN usuarios u ON l.cadastrado_por = u.id
                WHERE l.status_aprovacao = %s
                ORDER BY l.titulo
            """, (status_filtro,))
        else:
            cursor.execute("""
                SELECT l.id, l.titulo, l.autor, l.genero, l.ano_publicacao, l.imagem_url,
                       l.status_aprovacao, l.data_aprovacao, l.motivo_rejeicao,
                       u.nome as usuario_nome
                FROM livros l
                LEFT JOIN usuarios u ON l.cadastrado_por = u.id
                ORDER BY l.status_aprovacao, l.titulo
            """)

        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    livros = [
        {
            "id": row[0],
            "titulo": row[1],
            "autor": row[2],
            "genero": row[3],
            "ano_publicacao": row[4],
            "imagem_url": row[5],
            "status_aprovacao": row[6],
            "data_aprovacao": str(row[7]) if row[7] else None,
            "motivo_rejeicao": row[8],
            "cadastrado_por_nome": row[9]
        }
        for row in rows
    ]

    return jsonify({
        "total": len(livros),
        "livros": livros
    }), 200


@livrosRoute.route("/admin/<livro_id>", methods=["PUT"])
@requerir_admin
def editarLivroAdmin(admin_id, livro_id, **kwargs):
    """
    Admin pode editar qualquer livro.
    """
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Nenhum dado enviado"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM livros WHERE id = %s", (livro_id,))
        if not cursor.fetchone():
            return jsonify({"erro": "Livro não encontrado"}), 404

        cursor.execute("""
            UPDATE livros 
            SET titulo = COALESCE(%s, titulo),
                autor = COALESCE(%s, autor),
                genero = COALESCE(%s, genero),
                ano_publicacao = COALESCE(%s, ano_publicacao),
                imagem_url = COALESCE(%s, imagem_url)
            WHERE id = %s
            RETURNING id, titulo, autor, genero, ano_publicacao, imagem_url, status_aprovacao
        """, (
            dados.get("titulo"),
            dados.get("autor"),
            dados.get("genero"),
            dados.get("ano_publicacao"),
            dados.get("imagem_url"),
            livro_id
        ))

        row = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "mensagem": "Livro atualizado com sucesso!",
        "livro": {
            "id": row[0],
            "titulo": row[1],
            "autor": row[2],
            "genero": row[3],
            "ano_publicacao": row[4],
            "imagem_url": row[5],
            "status_aprovacao": row[6]
        }
    }), 200


@livrosRoute.route("/admin/<livro_id>", methods=["DELETE"])
@requerir_admin
def excluirLivroAdmin(admin_id, livro_id, **kwargs):
    """Admin pode excluir qualquer livro."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT titulo, status_aprovacao FROM livros WHERE id = %s", (livro_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"erro": "Livro não encontrado"}), 404

        titulo = row[0]
        status = row[1]

        # Verificar se há leituras associadas
        cursor.execute("SELECT COUNT(*) FROM leituras WHERE id_livro = %s", (livro_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            return jsonify({
                "erro": f"Não é possível excluir. Existem {count} leitura(s) associada(s) a este livro."
            }), 400

        cursor.execute("DELETE FROM livros WHERE id = %s", (livro_id,))
        conn.commit()

        # ✅ Se estava pendente, remove da fila
        if status == 'pendente':
            fila_aprovacao.remover_por_id(livro_id)

    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "mensagem": f"Livro '{titulo}' excluído com sucesso!"
    }), 200