from flask import Blueprint, render_template
from controllers.auth_utils import requerir_token
from flask import Blueprint, render_template, session, redirect, url_for
from database import bd
from flask import Blueprint, render_template, session

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
        return redirect(url_for("pages.homepage"))  # Redireciona se não logado

    usuario = bd.usuarios.get(usuario_id)
    return render_template("perfil.html", usuario=usuario)

@pagesRoute.route("/home_page_usuarios", methods=["GET"])
def home_page():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("pages.homepage"))  # Redireciona se não logado

    usuario = bd.usuarios.get(usuario_id)
    return render_template("home_page_usuarios.html", usuario=usuario)



@pagesRoute.route("/minhas_leituras") #somente leituras dos livros e pesquisa dos livros
def listar_livros():
    # Você pode pegar o usuario logado via session
    usuario_id = session.get("usuario_id")
    livros = list(bd.livros.values())  # pega todos os livros
    return render_template("minhas_leituras.html", livros=livros, usuario_id=usuario_id)

# Endpoint para pesquisar livros via fetch
@pagesRoute.route("/pesquisar_livros")
def pesquisar_livros():
    query = request.args.get("q", "").lower()
    resultado = [
        livro.__dict__ for livro in bd.livros.values()
        if query in livro.titulo.lower() or query in livro.autor.lower() or query in livro.genero.lower()
    ]
    return jsonify(resultado)

@pagesRoute.route("/crudes_livros")  # crud de livros
def pagina_listar_livros():
    # Você pode pegar o usuario logado via session
    usuario_id = session.get("usuario_id")
    livros = list(bd.livros.values())  # pega todos os livros
    return render_template("gerenciar_livros.html", livros=livros, usuario_id=usuario_id)
