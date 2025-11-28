from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from dbpostgres import bd

# Blueprint para páginas HTML
pagesRoute = Blueprint("pages", __name__)

# ------------------------------------------------------------
# Homepage (acessível sem login)
@pagesRoute.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")


# ------------------------------------------------------------
# Página de perfil
@pagesRoute.route("/perfil", methods=["GET"])
def perfil_usuario():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("pages.homepage"))

    cursor = bd.conn.cursor()
    cursor.execute("SELECT id, nome, email FROM usuarios WHERE id = %s", (usuario_id,))
    usuario = cursor.fetchone()
    cursor.close()

    return render_template("perfil.html", usuario=usuario)


# ------------------------------------------------------------
@pagesRoute.route("/home_page_usuarios", methods=["GET"])
def home_page():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("pages.homepage"))

    cursor = bd.conn.cursor()
    cursor.execute("SELECT id, nome FROM usuarios WHERE id = %s", (usuario_id,))
    usuario = cursor.fetchone()
    cursor.close()

    return render_template("home_page_usuarios.html", usuario=usuario)


# ------------------------------------------------------------
# Página: Minhas leituras + pesquisa
@pagesRoute.route("/minhas_leituras")
def listar_livros():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("pages.homepage"))

    cursor = bd.conn.cursor()
    cursor.execute("SELECT id, titulo, autor, genero FROM livros")
    livros = cursor.fetchall()
    cursor.close()

    return render_template("minhas_leituras.html", livros=livros, usuario_id=usuario_id)


# ------------------------------------------------------------
# Endpoint ajax de pesquisa
@pagesRoute.route("/pesquisar_livros")
def pesquisar_livros():
    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify([])

    cursor = bd.conn.cursor()
    cursor.execute("""
        SELECT id, titulo, autor, genero
        FROM livros
        WHERE LOWER(titulo) LIKE %s
           OR LOWER(autor)  LIKE %s
           OR LOWER(genero) LIKE %s
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))

    livros = cursor.fetchall()
    cursor.close()

    resultado = [
        {"id": l[0], "titulo": l[1], "autor": l[2], "genero": l[3]}
        for l in livros
    ]

    return jsonify(resultado)


# ------------------------------------------------------------
# Página CRUD de livros
@pagesRoute.route("/crudes_livros")
def pagina_listar_livros():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("pages.homepage"))

    cursor = bd.conn.cursor()
    cursor.execute("SELECT id, titulo, autor, genero FROM livros")
    livros = cursor.fetchall()
    cursor.close()

    return render_template("gerenciar_livros.html", livros=livros, usuario_id=usuario_id)
