"""
Adaptador que converte o PostgreSQL para a interface esperada pelo sistema de IA.
"""

from dbpostgres import get_connection


class LivroObj:
    """Objeto que simula a classe Livro para o sistema de IA."""

    def __init__(self, row):
        self.id = row[0]
        self.titulo = row[1]
        self.autor = row[2]
        self.genero = row[3]
        self.ano_publicacao = row[4]
        self.ano = row[4]
        self.imagem_url = row[5]
        self.status_aprovacao = row[6] if len(row) > 6 else 'aprovado'


class LeituraObj:
    """Objeto que simula a classe Leitura para o sistema de IA."""

    def __init__(self, row):
        self.id = row[0]
        self.id_usuario = row[1]
        self.id_livro = row[2]
        self.status = row[3]
        self.avaliacao = row[4]
        self.data_leitura = row[5]
        self.comentario = row[6] if len(row) > 6 else None


class BancoDadosAdapter:
    """
    Adaptador que fornece a interface esperada pelo recommendation_knn.py
    usando PostgreSQL como backend.
    """

    def __init__(self):
        self._livros = None
        self._usuarios = None
        self._cache_valido = False

    def _carregar_cache(self):
        """Carrega dados do PostgreSQL para cache."""
        if self._cache_valido:
            return

        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Carregar livros aprovados
                cursor.execute("""
                    SELECT id, titulo, autor, genero, ano_publicacao, imagem_url, status_aprovacao
                    FROM livros
                    WHERE status_aprovacao = 'aprovado'
                """)
                self._livros = {}
                for row in cursor.fetchall():
                    livro = LivroObj(row)
                    self._livros[livro.id] = livro

                # Carregar usuários
                cursor.execute("SELECT id FROM usuarios")
                self._usuarios = {row[0]: True for row in cursor.fetchall()}

                self._cache_valido = True
                print(f"📚 Cache IA carregado: {len(self._livros)} livros, {len(self._usuarios)} usuários")

            finally:
                cursor.close()

    def invalidar_cache(self):
        """Invalida o cache para forçar recarregamento."""
        self._cache_valido = False
        self._livros = None
        self._usuarios = None

    @property
    def livros(self):
        """Retorna dicionário de livros {id: LivroObj}."""
        self._carregar_cache()
        return self._livros

    @property
    def usuarios(self):
        """Retorna dicionário de usuários {id: True}."""
        self._carregar_cache()
        return self._usuarios

    def buscarLivroPorId(self, livro_id):
        """Busca um livro pelo ID."""
        self._carregar_cache()
        return self._livros.get(livro_id)

    def carregarLeituras(self, usuario_id):
        """Carrega todas as leituras de um usuário."""
        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT id, id_usuario, id_livro, status, avaliacao, data_leitura, comentario
                    FROM leituras
                    WHERE id_usuario = %s
                """, (usuario_id,))

                leituras = [LeituraObj(row) for row in cursor.fetchall()]
                return leituras

            finally:
                cursor.close()

    def obter_estatisticas(self):
        """Retorna estatísticas do banco para debug."""
        self._carregar_cache()

        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM leituras WHERE avaliacao IS NOT NULL")
                total_avaliacoes = cursor.fetchone()[0]

                return {
                    "total_livros": len(self._livros),
                    "total_usuarios": len(self._usuarios),
                    "total_avaliacoes": total_avaliacoes
                }
            finally:
                cursor.close()


# Instância global (singleton)
bd_adapter = BancoDadosAdapter()