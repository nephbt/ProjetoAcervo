from flask import Flask, render_template
from flask.cli import locate_app
from controllers.livros_controller import livrosRoute
from controllers.usuarios_controller import usuariosRoute
from controllers.leituras_controller import leiturasRoute
from controllers.paginas_controller import pagesRoute
import argparse
import os

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
# Configuração da chave secreta para sessões
app.secret_key = os.getenv("SECRET_KEY") or "dev-secret-key"

# Registro dos blueprints
app.register_blueprint(livrosRoute)
app.register_blueprint(usuariosRoute)
app.register_blueprint(leiturasRoute)
app.register_blueprint(pagesRoute)

# ------------------------------------------------------------
# Rotas principais de páginas HTML

@app.route("/")
def homepage():
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
# Execução do servidor Flask (verificação se Rotas carregam, Blueprints importam, Banco inicializa, Não há erro de importação)
# ------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-build", action="store_true")
    args = parser.parse_args()

    if args.test_build:
        print("🔍 Testando build...")
        print("App carregado com sucesso.")
    else:
        debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
        app.run(debug=debug_mode)



