from flask import Flask, render_template
from controllers.livros_controller import livrosRoute
from controllers.usuarios_controller import usuariosRoute
from controllers.leituras_controller import leiturasRoute
from controllers.paginas_controller import pagesRoute

# ------------------------------------------------------------
#  ROTAS DE TESTE / FORMULÁRIOS HTML
# ------------------------------------------------------------
# Para acessar as páginas no navegador:
#  - Cadastro de usuários: http://127.0.0.1:5000/cadastro_usuario
#  - API de usuários (JSON): http://127.0.0.1:5000/usuarios
#  - Cadastro de livros: http://127.0.0.1:5000/cadastro_livro
#  - API de livros (JSON): http://127.0.0.1:5000/livros
# ------------------------------------------------------------

app = Flask(__name__)
app.secret_key = "chave_muito_secreta"

# Registro dos blueprints
app.register_blueprint(livrosRoute)
app.register_blueprint(usuariosRoute)
app.register_blueprint(leiturasRoute)
app.register_blueprint(pagesRoute)

# ------------------------------------------------------------
# Rotas principais de páginas HTML

@app.route("/")
def homepage():
    # Aqui futuramente você pode retornar seu "index.html"
    return render_template("index.html")

@app.route("/login_usuario")
def login_usuario():
    # Página de login (formulário HTML)
    return render_template("login.html")

@app.route("/cadastro_usuario")
def cadastro_usuario():
    # Página de cadastro de usuários
    return render_template("cadastro_usuario.html")

@app.route("/cadastro_livro")
def cadastro_livro():
    # Página de cadastro de livros
    return render_template("cadastro_livro.html")

# ------------------------------------------------------------
# Execução do servidor Flask
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
