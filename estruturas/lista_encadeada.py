"""
Estrutura de Dados: Lista Encadeada
Aplicação: Histórico de leituras dos usuários.
Cada usuário tem sua própria lista de leituras.
"""


class NoLeitura:
    """
    Nó da lista encadeada.
    Cada nó contém os dados da leitura e um ponteiro para o próximo.
    """

    def __init__(self, leitura):
        self.dados = leitura  # Dicionário com dados da leitura
        self.proximo = None  # Ponteiro para o próximo nó


class ListaLeituras:
    """
    Lista Encadeada de Leituras.

    Estrutura:
    [cabeça] → [nó1] → [nó2] → [nó3] → None

    Operações:
    - adicionar_inicio: O(1) - leitura mais recente primeiro
    - adicionar_fim: O(n) - leitura mais antiga primeiro
    - remover: O(n) - busca e remove
    - buscar: O(n) - busca por id do livro
    - listar: O(n) - retorna todas as leituras
    """

    def __init__(self):
        self.cabeca = None  # Primeiro nó da lista
        self._tamanho = 0

    def adicionar_inicio(self, leitura):
        """
        Adiciona leitura no INÍCIO da lista (mais recente primeiro).
        Complexidade: O(1)

        Antes: [A] → [B] → [C] → None
        Depois: [NOVO] → [A] → [B] → [C] → None
        """
        novo_no = NoLeitura(leitura)
        novo_no.proximo = self.cabeca
        self.cabeca = novo_no
        self._tamanho += 1

        titulo = leitura.get('titulo_livro', leitura.get('id_livro', 'Livro'))
        print(f"📖 Leitura '{titulo}' adicionada no início da lista")

    def adicionar_fim(self, leitura):
        """
        Adiciona leitura no FIM da lista.
        Complexidade: O(n) - precisa percorrer até o final

        Antes: [A] → [B] → [C] → None
        Depois: [A] → [B] → [C] → [NOVO] → None
        """
        novo_no = NoLeitura(leitura)

        if self.esta_vazia():
            self.cabeca = novo_no
        else:
            atual = self.cabeca
            while atual.proximo:
                atual = atual.proximo
            atual.proximo = novo_no

        self._tamanho += 1
        titulo = leitura.get('titulo_livro', leitura.get('id_livro', 'Livro'))
        print(f"📖 Leitura '{titulo}' adicionada no fim da lista")

    def remover(self, id_livro):
        """
        Remove uma leitura pelo ID do livro.
        Complexidade: O(n)

        Retorna True se removeu, False se não encontrou.
        """
        if self.esta_vazia():
            return False

        # Se for o primeiro nó
        if self.cabeca.dados.get('id_livro') == id_livro:
            removido = self.cabeca.dados
            self.cabeca = self.cabeca.proximo
            self._tamanho -= 1
            print(f"🗑️ Leitura removida da lista")
            return True

        # Busca no resto da lista
        atual = self.cabeca
        while atual.proximo:
            if atual.proximo.dados.get('id_livro') == id_livro:
                removido = atual.proximo.dados
                atual.proximo = atual.proximo.proximo
                self._tamanho -= 1
                print(f"🗑️ Leitura removida da lista")
                return True
            atual = atual.proximo

        return False

    def remover_por_id(self, leitura_id):
        """
        Remove uma leitura pelo ID da própria leitura.
        Complexidade: O(n)
        """
        if self.esta_vazia():
            return False

        # Se for o primeiro nó
        if self.cabeca.dados.get('id') == leitura_id:
            self.cabeca = self.cabeca.proximo
            self._tamanho -= 1
            return True

        # Busca no resto da lista
        atual = self.cabeca
        while atual.proximo:
            if atual.proximo.dados.get('id') == leitura_id:
                atual.proximo = atual.proximo.proximo
                self._tamanho -= 1
                return True
            atual = atual.proximo

        return False

    def buscar(self, id_livro):
        """
        Busca uma leitura pelo ID do livro.
        Complexidade: O(n)

        Retorna o dicionário da leitura ou None.
        """
        atual = self.cabeca
        posicao = 1

        while atual:
            if atual.dados.get('id_livro') == id_livro:
                return {
                    'leitura': atual.dados,
                    'posicao': posicao
                }
            atual = atual.proximo
            posicao += 1

        return None

    def buscar_por_id(self, leitura_id):
        """
        Busca uma leitura pelo ID da leitura.
        Complexidade: O(n)
        """
        atual = self.cabeca

        while atual:
            if atual.dados.get('id') == leitura_id:
                return atual.dados
            atual = atual.proximo

        return None

    def atualizar(self, id_livro, novos_dados):
        """
        Atualiza uma leitura existente.
        Complexidade: O(n)
        """
        atual = self.cabeca

        while atual:
            if atual.dados.get('id_livro') == id_livro:
                # Atualiza apenas os campos fornecidos
                for chave, valor in novos_dados.items():
                    if valor is not None:
                        atual.dados[chave] = valor
                return True
            atual = atual.proximo

        return False

    def listar(self):
        """
        Retorna todas as leituras em ordem (da mais recente para mais antiga).
        Complexidade: O(n)
        """
        leituras = []
        atual = self.cabeca
        posicao = 1

        while atual:
            leitura = dict(atual.dados)
            leitura['posicao_lista'] = posicao
            leituras.append(leitura)
            atual = atual.proximo
            posicao += 1

        return leituras

    def contar_por_status(self, status):
        """
        Conta leituras por status (lido, lendo, quero_ler).
        Complexidade: O(n)
        """
        contador = 0
        atual = self.cabeca

        while atual:
            if atual.dados.get('status') == status:
                contador += 1
            atual = atual.proximo

        return contador

    def filtrar_por_status(self, status):
        """
        Retorna leituras filtradas por status.
        Complexidade: O(n)
        """
        leituras = []
        atual = self.cabeca

        while atual:
            if atual.dados.get('status') == status:
                leituras.append(atual.dados)
            atual = atual.proximo

        return leituras

    def obter_estatisticas(self):
        """
        Retorna estatísticas das leituras.
        Complexidade: O(n)
        """
        stats = {
            'total': 0,
            'lidos': 0,
            'lendo': 0,
            'quero_ler': 0,
            'soma_avaliacoes': 0,
            'qtd_avaliacoes': 0
        }

        atual = self.cabeca
        while atual:
            stats['total'] += 1
            status = atual.dados.get('status', '')

            if status == 'lido':
                stats['lidos'] += 1
            elif status == 'lendo':
                stats['lendo'] += 1
            elif status == 'quero_ler':
                stats['quero_ler'] += 1

            avaliacao = atual.dados.get('avaliacao')
            if avaliacao is not None and avaliacao > 0:
                stats['soma_avaliacoes'] += avaliacao
                stats['qtd_avaliacoes'] += 1

            atual = atual.proximo

        # Calcula média
        if stats['qtd_avaliacoes'] > 0:
            stats['media_avaliacao'] = round(stats['soma_avaliacoes'] / stats['qtd_avaliacoes'], 2)
        else:
            stats['media_avaliacao'] = 0

        return stats

    def esta_vazia(self):
        """Verifica se a lista está vazia."""
        return self.cabeca is None

    def tamanho(self):
        """Retorna o número de leituras na lista."""
        return self._tamanho

    def contem(self, id_livro):
        """Verifica se já existe leitura para este livro."""
        return self.buscar(id_livro) is not None

    def __len__(self):
        return self._tamanho

    def __str__(self):
        if self.esta_vazia():
            return "Lista vazia"

        titulos = []
        atual = self.cabeca
        while atual:
            titulo = atual.dados.get('titulo_livro', atual.dados.get('id_livro', '?'))
            titulos.append(titulo)
            atual = atual.proximo

        return f"Lista [{self._tamanho}]: " + " → ".join(titulos)

    def __iter__(self):
        """Permite iterar sobre a lista com for."""
        atual = self.cabeca
        while atual:
            yield atual.dados
            atual = atual.proximo


class GerenciadorLeituras:
    """
    Gerencia as listas de leituras de TODOS os usuários.
    Usa um dicionário onde a chave é o ID do usuário.

    Estrutura:
    {
        "usuario_1": ListaLeituras(),
        "usuario_2": ListaLeituras(),
        ...
    }
    """

    def __init__(self):
        self.leituras_por_usuario = {}  # {usuario_id: ListaLeituras}

    def obter_lista(self, usuario_id):
        """Obtém ou cria a lista de leituras de um usuário."""
        if usuario_id not in self.leituras_por_usuario:
            self.leituras_por_usuario[usuario_id] = ListaLeituras()
        return self.leituras_por_usuario[usuario_id]

    def adicionar_leitura(self, usuario_id, leitura):
        """Adiciona leitura na lista do usuário."""
        lista = self.obter_lista(usuario_id)
        lista.adicionar_inicio(leitura)

    def remover_leitura(self, usuario_id, id_livro):
        """Remove leitura da lista do usuário."""
        lista = self.obter_lista(usuario_id)
        return lista.remover(id_livro)

    def buscar_leitura(self, usuario_id, id_livro):
        """Busca leitura na lista do usuário."""
        lista = self.obter_lista(usuario_id)
        resultado = lista.buscar(id_livro)
        return resultado['leitura'] if resultado else None

    def listar_leituras(self, usuario_id):
        """Lista todas as leituras do usuário."""
        lista = self.obter_lista(usuario_id)
        return lista.listar()

    def estatisticas_usuario(self, usuario_id):
        """Retorna estatísticas do usuário."""
        lista = self.obter_lista(usuario_id)
        return lista.obter_estatisticas()

    def total_usuarios(self):
        """Retorna quantos usuários têm leituras."""
        return len(self.leituras_por_usuario)

    def total_leituras(self):
        """Retorna o total de leituras de todos os usuários."""
        total = 0
        for lista in self.leituras_por_usuario.values():
            total += lista.tamanho()
        return total