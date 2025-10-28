from flask import Flask, request, jsonify, redirect, url_for, session, Blueprint
from flask import render_template
from controllers import usuariosRoute, livrosRoute, leiturasRoute

# ------------------------------------------------------------
# PARA ACESSAR A PAGINA DOS CADASTROS VC PRECISA ACESSAR PELOS ENDPOINTS.

# CADASTROS USUARIOS: http://127.0.0.1:5000/cadastro_usuario
# ACESSAR AS INFORMAÇÕES DO BANCO DE DADOS DE USUARIOS JSON:http://127.0.0.1:5000/usuarios

# CADASTROS LIVROS: http://127.0.0.1:5000/cadastro_livro
# ACESSAR AS INFORMAÇÕES DO BANCO DE DADOS DE LIVROS JSON: http://127.0.0.1:5000/livros
#-------------------------------------------------------------

app = Flask(__name__)
app.register_blueprint(livrosRoute)
app.register_blueprint(usuariosRoute)
app.register_blueprint(leiturasRoute)

@app.route("/")
def homepage():
    # Retornar index.html aqui
    return "oi sou um placeholder"

@app.route("/entrar")
def loginECadastro():
    # Retornar html da página de login/cadastro
    return "oi sou outro placeholder"

# Endpoint serve para renderizar o formulário em html para pegar os dados do usuario
@app.route("/cadastro_usuario")
def paginaCadastroUsuario():
    return render_template("cadastro_usuario.html")

# Renderiza o formulário no html
@app.route("/cadastro_livro")
def paginaCadastroLivro():
    return render_template("cadastro_livro.html")


if __name__ == '__main__':
    app.run(debug=True)