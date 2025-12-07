"""
Estrutura de Dados: Fila (FIFO - First In, First Out)
Aplicação: Fila de aprovação de livros pendentes.
O primeiro livro cadastrado é o primeiro a ser avaliado pelo admin.
"""


class No:
    """Nó da fila encadeada."""

    def __init__(self, dados):
        self.dados = dados
        self.proximo = None


class FilaAprovacao:
    """
    Fila de livros aguardando aprovação.
    Implementação com lista encadeada para demonstrar a estrutura.

    Operações:
    - enfileirar: O(1) - adiciona no final
    - desenfileirar: O(1) - remove do início
    - primeiro: O(1) - consulta o primeiro
    """

    def __init__(self):
        self.inicio = None  # Primeiro da fila (próximo a ser atendido)
        self.fim = None  # Último da fila
        self._tamanho = 0

    def enfileirar(self, livro):
        """
        Adiciona um livro no final da fila.
        Complexidade: O(1)
        """
        novo_no = No(livro)

        if self.esta_vazia():
            self.inicio = novo_no
            self.fim = novo_no
        else:
            self.fim.proximo = novo_no
            self.fim = novo_no

        self._tamanho += 1
        print(f"📥 Livro '{livro.get('titulo', livro)}' entrou na fila. Posição: {self._tamanho}")

    def desenfileirar(self):
        """
        Remove e retorna o primeiro livro da fila (mais antigo).
        Complexidade: O(1)
        """
        if self.esta_vazia():
            print("⚠️ Fila vazia!")
            return None

        livro = self.inicio.dados
        self.inicio = self.inicio.proximo

        if self.inicio is None:
            self.fim = None

        self._tamanho -= 1
        print(f"📤 Livro '{livro.get('titulo', livro)}' saiu da fila para avaliação.")
        return livro

    def primeiro(self):
        """
        Retorna o primeiro livro sem remover.
        Complexidade: O(1)
        """
        if self.esta_vazia():
            return None
        return self.inicio.dados

    def esta_vazia(self):
        """Verifica se a fila está vazia."""
        return self.inicio is None

    def tamanho(self):
        """Retorna a quantidade de livros na fila."""
        return self._tamanho

    def listar(self):
        """
        Retorna todos os livros da fila em ordem (sem remover).
        Complexidade: O(n)
        """
        livros = []
        atual = self.inicio
        posicao = 1

        while atual:
            livro_com_posicao = dict(atual.dados)
            livro_com_posicao['posicao_fila'] = posicao
            livros.append(livro_com_posicao)
            atual = atual.proximo
            posicao += 1

        return livros

    def buscar_por_id(self, livro_id):
        """
        Busca um livro na fila pelo ID.
        Complexidade: O(n)
        """
        atual = self.inicio
        posicao = 1

        while atual:
            if atual.dados.get('id') == livro_id:
                return {'livro': atual.dados, 'posicao': posicao}
            atual = atual.proximo
            posicao += 1

        return None

    def remover_por_id(self, livro_id):
        """
        Remove um livro específico da fila (quando aprovado/rejeitado).
        Complexidade: O(n)
        """
        if self.esta_vazia():
            return False

        # Se for o primeiro
        if self.inicio.dados.get('id') == livro_id:
            self.desenfileirar()
            return True

        # Busca no resto da fila
        atual = self.inicio
        while atual.proximo:
            if atual.proximo.dados.get('id') == livro_id:
                # Remove o nó
                if atual.proximo == self.fim:
                    self.fim = atual
                atual.proximo = atual.proximo.proximo
                self._tamanho -= 1
                return True
            atual = atual.proximo

        return False

    def __str__(self):
        """Representação da fila."""
        if self.esta_vazia():
            return "Fila vazia"

        livros = []
        atual = self.inicio
        while atual:
            livros.append(atual.dados.get('titulo', str(atual.dados)))
            atual = atual.proximo

        return f"Fila [{self._tamanho}]: " + " → ".join(livros)

    def __len__(self):
        return self._tamanho