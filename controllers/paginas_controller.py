from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from dbpostgres import get_connection

pagesRoute = Blueprint("pages", __name__)


# ============================================================
# HELPERS
# ============================================================

def obter_todos_livros():
    """
    Retorna todos os livros aprovados do banco de dados.
    """
    with get_connection() as conn:
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

    return [
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


# ============================================================
# PÁGINAS PÚBLICAS
# ============================================================

@pagesRoute.route("/login_usuario", methods=["GET"])
def pagina_login():
    """Página de login."""
    return render_template("login.html")


@pagesRoute.route("/cadastro_usuario", methods=["GET"])
def pagina_cadastro():
    """Página de cadastro."""
    return render_template("cadastro_usuario.html")


# ============================================================
# PÁGINAS PROTEGIDAS
# ============================================================

@pagesRoute.route("/perfil", methods=["GET"])
def perfil_usuario():
    """Página de perfil do usuário logado."""
    return render_template("perfil.html", usuario={})


@pagesRoute.route("/home_page_usuarios", methods=["GET"])
def home_page():
    """Home page para usuários logados."""
    return render_template("home_page_usuarios.html", usuario={})


@pagesRoute.route("/home_page_admin", methods=["GET"])
def home_page_admin():
    """Home page para administradores."""
    return render_template("home_page_admin.html")


@pagesRoute.route("/minhas_leituras", methods=["GET"])
def listar_leituras():
    """Página de leituras do usuário."""
    return render_template("minhas_leituras.html", livros=[])


@pagesRoute.route("/crudes_livros", methods=["GET"])
def pagina_listar_livros():
    """Página de gerenciamento de livros (CRUD)."""
    livros = obter_todos_livros()
    return render_template("gerenciar_livros.html", livros=livros)


@pagesRoute.route("/sobre")
def pagina_sobre():
    return render_template("sobre.html")


# ============================================================
# ENDPOINTS AJAX
# ============================================================

@pagesRoute.route("/pesquisar_livros", methods=["GET"])
def pesquisar_livros():
    """
    Pesquisa livros aprovados por título, autor ou gênero.
    """
    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify([])

    with get_connection() as conn:
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

    resultado = [
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

    return jsonify(resultado)