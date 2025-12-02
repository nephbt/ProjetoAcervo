from flask import Flask, render_template
from extensions import db
from controllers.livros_controller import livrosRoute
from controllers.usuarios_controller import usuariosRoute
from controllers.leituras_controller import leiturasRoute
from controllers.paginas_controller import pagesRoute
from controllers.recommendation_controller import recommendationRoute

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
app.register_blueprint(recommendationRoute)

def create_app():
    """Factory para criar a aplicação Flask com configurações corretas"""
    app = Flask(__name__)
    app.secret_key = "chave_muito_secreta"

    # Configuração do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leituras.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar SQLAlchemy com a app
    db.init_app(app)

    # Registro dos blueprints
    app.register_blueprint(livrosRoute)
    app.register_blueprint(usuariosRoute)
    app.register_blueprint(leiturasRoute)
    app.register_blueprint(pagesRoute)
    app.register_blueprint(recommendationRoute)

    # Rotas principais de páginas HTML
    @app.route("/")
    def homepage():
        return render_template("index.html")

    @app.route("/login_usuario")
    def login_usuario():
        return render_template("login.html")

    @app.route("/cadastro_usuario")
    def cadastro_usuario():
        return render_template("cadastro_usuario.html")

    @app.route("/cadastro_livro")
    def cadastro_livro():
        return render_template("cadastro_livro.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)