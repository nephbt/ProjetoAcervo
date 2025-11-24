import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


# ============================================================
# 1. Construção dos vetores de features dos livros
# ============================================================

def construir_vetores_livros(bd):
    """
    Constrói vetores de features para cada livro usando:
      - autor (one-hot)
      - genero (one-hot, multi-label)
      - ano_publicacao (normalizado)
      - nota_media (normalizada, calculada a partir das leituras dos usuários)
    Retorna: vetores(dict id -> vetor), ids(list ordenada), lista_de_livros (objetos)
    """

    # Carregar livros (objeto do seu BD)
    livros = [bd.buscarLivroPorId(lid) for lid in bd.livros.keys()]
    livros = [l for l in livros if l is not None]

    if not livros:
        return {}, [], []

    # --- calcular nota média por livro iterando todas as leituras disponíveis ---
    avaliacoes_por_livro = defaultdict(list)
    for uid in bd.usuarios.keys():
        leituras = bd.carregarLeituras(uid) or []
        for lt in leituras:
            if getattr(lt, "avaliacao", None) is not None:
                avaliacoes_por_livro[lt.id_livro].append(lt.avaliacao)

    nota_media_por_livro = {}
    for l in livros:
        notas = avaliacoes_por_livro.get(l.id, [])
        nota_media_por_livro[l.id] = float(sum(notas) / len(notas)) if notas else 0.0

    # --- coleções únicas para autores e gêneros ---
    autores = sorted({(l.autor or "").strip() for l in livros})
    generos = sorted({g.strip() for l in livros for g in ((l.genero or "").split(",")) if g.strip()})

    map_autor = {a: i for i, a in enumerate(autores)}
    map_genero = {g: i for i, g in enumerate(generos)}

    # --- Ano e nota (arrays para normalizar) ---
    # pegar ano com fallback para nome diferente
    anos_list = []
    notas_list = []
    for l in livros:
        ano_val = getattr(l, "ano_publicacao", None)
        if ano_val is None:
            ano_val = getattr(l, "ano", None)
        # se ainda None, coloca 0
        anos_list.append(float(ano_val) if ano_val is not None else 0.0)
        notas_list.append(float(nota_media_por_livro.get(l.id, 0.0)))

    anos = np.array(anos_list).reshape(-1, 1)
    notas = np.array(notas_list).reshape(-1, 1)

    # Se todos anos forem iguais ou todos zeros, MinMaxScaler pode retornar zeros -> ok
    scaler_ano = MinMaxScaler()
    scaler_nota = MinMaxScaler()

    anos_norm = scaler_ano.fit_transform(anos)
    notas_norm = scaler_nota.fit_transform(notas)

    vetores = {}
    ids = []

    for idx, l in enumerate(livros):
        # autor one-hot (se autor desconhecido, vetor todo zero)
        vec_autor = np.zeros(len(autores))
        autor_key = (l.autor or "").strip()
        if autor_key in map_autor:
            vec_autor[map_autor[autor_key]] = 1

        # generos multi-hot
        vec_gen = np.zeros(len(generos))
        for g in (l.genero or "").split(","):
            g = g.strip()
            if g and g in map_genero:
                vec_gen[map_genero[g]] = 1

        ano_val = float(anos_norm[idx][0])
        nota_val = float(notas_norm[idx][0])

        vetor_final = np.concatenate([vec_autor, vec_gen, [ano_val], [nota_val]])
        vetores[l.id] = vetor_final
        ids.append(l.id)

    return vetores, ids, livros


def matriz_similaridade_itens(vetores, ids):
    if not ids:
        return None

    matriz = cosine_similarity([vetores[i] for i in ids])
    return matriz


# ============================================================
# 2. Recomendação item-based
# ============================================================

def recomendar_item_based(usuario_id, bd, num_recomendacoes=6, k=15):
    """
    Recomenda livros baseado em item similarity.

    Args:
        usuario_id: ID do usuário
        bd: Instância do banco de dados
        num_recomendacoes: Quantos livros recomendar
        k: Quantos livros similares considerar de cada livro lido
    """
    vetores, ids, _ = construir_vetores_livros(bd)

    if not vetores:
        return recomendar_livros_populares(bd, num_recomendacoes)

    matriz = matriz_similaridade_itens(vetores, ids)
    id_to_index = {lid: idx for idx, lid in enumerate(ids)}

    # ✅ CORREÇÃO: Não usar bd.carregarLeituras direto, pois retorna TODAS as leituras
    # Em vez disso, usar os dados já separados em treino/teste se disponível
    # Para uso em produção (sem treino/teste), usar apenas leituras com avaliação
    leituras = bd.carregarLeituras(usuario_id)
    if not leituras:
        return recomendar_livros_populares(bd, num_recomendacoes)

    # Considerar apenas livros com avaliação (indicam interesse real)
    livros_lidos = [l.id_livro for l in leituras if getattr(l, 'avaliacao', None) is not None]
    livros_lidos = [lid for lid in livros_lidos if lid in vetores]

    if not livros_lidos:
        return recomendar_livros_populares(bd, num_recomendacoes)

    score_acumulado = defaultdict(float)

    for lid in livros_lidos:
        if lid not in id_to_index:
            continue

        idx = id_to_index[lid]

        similares = list(enumerate(matriz[idx]))
        similares = sorted(similares, key=lambda x: x[1], reverse=True)

        # ✅ CORREÇÃO: Usar range(1, k+1) para pegar posições 1 a k (pulando o próprio livro em posição 0)
        for i, sim in similares[1:k + 1]:
            outro = ids[i]
            if outro not in livros_lidos:
                score_acumulado[outro] += sim

    ordenados = sorted(score_acumulado.items(), key=lambda x: x[1], reverse=True)

    recomendados = [lid for lid, _ in ordenados[:num_recomendacoes]]

    if len(recomendados) < num_recomendacoes:
        populares = recomendar_livros_populares(bd, num_recomendacoes)
        for p in populares:
            if p not in recomendados:
                recomendados.append(p)

    return recomendados[:num_recomendacoes]


def recomendar_livros_knn(usuario_id, bd, num_recomendacoes=6, n_neighbors=10):
    """Alias para recomendar_item_based com nome alternativo"""
    return recomendar_item_based(usuario_id, bd, num_recomendacoes, n_neighbors)


# ============================================================
# 3. Fallback: recomenda livros populares
# ============================================================

def recomendar_livros_populares(bd, num_recomendacoes=6):
    avaliacoes = defaultdict(list)

    for uid in bd.usuarios:
        for l in bd.carregarLeituras(uid):
            if l.avaliacao is not None:
                avaliacoes[l.id_livro].append(l.avaliacao)

    medias = [(lid, sum(notas) / len(notas)) for lid, notas in avaliacoes.items() if notas]

    medias.sort(key=lambda x: x[1], reverse=True)

    return [lid for lid, _ in medias[:num_recomendacoes]]


# ============================================================
# 4. Gerador de dados de treino e teste
# ============================================================

def gerar_train_test(bd, test_size=0.3):
    treino = {}
    teste = {}

    for uid in bd.usuarios.keys():
        leituras = [
            (l.id_livro, l.avaliacao)
            for l in bd.carregarLeituras(uid)
            if l.avaliacao is not None
        ]

        if len(leituras) < 2:
            continue

        train_u, test_u = train_test_split(
            leituras,
            test_size=test_size,
            random_state=42
        )

        treino[uid] = train_u
        teste[uid] = test_u

    return treino, teste


# ============================================================
# 5. Métricas e avaliação
# ============================================================

def precision_at_k(recomendacoes, itens_reais, k=5):
    """
    Calcula precision@k

    Args:
        recomendacoes: Lista de IDs recomendados
        itens_reais: Lista de (id, nota) dos itens reais
        k: Quantos itens considerar
    """
    k = min(k, len(recomendacoes))
    if k == 0:
        return 0.0

    recomendados = set(recomendacoes[:k])
    verdadeiros = {lid for lid, nota in itens_reais}

    acertos = len(recomendados & verdadeiros)
    return acertos / k


def recomendar_item_based_com_treino(usuario_id, bd, livros_treino_ids, num_recomendacoes=6, k=3):
    """
    Versão de recomendar_item_based que usa apenas livros de treino.
    Útil para avaliação do modelo.

    Args:
        usuario_id: ID do usuário
        bd: Instância do banco de dados
        livros_treino_ids: Lista de IDs de livros do treino
        num_recomendacoes: Quantos livros recomendar
        k: Quantos livros similares considerar de cada livro lido
    """
    vetores, ids, _ = construir_vetores_livros(bd)

    if not vetores or not livros_treino_ids:
        return recomendar_livros_populares(bd, num_recomendacoes)

    matriz = matriz_similaridade_itens(vetores, ids)
    id_to_index = {lid: idx for idx, lid in enumerate(ids)}

    # Usar apenas livros do treino
    livros_lidos = [lid for lid in livros_treino_ids if lid in vetores]

    if not livros_lidos:
        return recomendar_livros_populares(bd, num_recomendacoes)

    score_acumulado = defaultdict(float)

    for lid in livros_lidos:
        if lid not in id_to_index:
            continue

        idx = id_to_index[lid]
        similares = list(enumerate(matriz[idx]))
        similares = sorted(similares, key=lambda x: x[1], reverse=True)

        for i, sim in similares[1:k + 1]:
            outro = ids[i]
            if outro not in livros_lidos:
                score_acumulado[outro] += sim

    ordenados = sorted(score_acumulado.items(), key=lambda x: x[1], reverse=True)
    recomendados = [lid for lid, _ in ordenados[:num_recomendacoes]]

    if len(recomendados) < num_recomendacoes:
        populares = recomendar_livros_populares(bd, num_recomendacoes)
        for p in populares:
            if p not in recomendados:
                recomendados.append(p)

    return recomendados[:num_recomendacoes]


def avaliar_modelo(bd, k=5):
    """
    Avalia o modelo de recomendação usando precision@k
    """
    treino, teste = gerar_train_test(bd)
    scores = []

    print("Usuários no teste:", len(teste))
    for uid, livros in teste.items():
        print(uid, "tem", len(livros), "livros no teste e", len(treino.get(uid, [])), "no treino")

    for usuario_id in treino.keys():
        if usuario_id not in teste:
            continue

        # ✅ Usar apenas livros de treino para recomendação
        livros_treino = [l[0] for l in treino[usuario_id]]
        rec = recomendar_item_based_com_treino(usuario_id, bd, livros_treino, num_recomendacoes=k, k=k)
        score = precision_at_k(rec, teste[usuario_id], k)
        scores.append(score)

    if not scores:
        return 0

    return sum(scores) / len(scores)