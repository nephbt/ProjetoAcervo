import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split, KFold
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
    anos_list = []
    notas_list = []
    for l in livros:
        ano_val = getattr(l, "ano_publicacao", None)
        if ano_val is None:
            ano_val = getattr(l, "ano", None)
        anos_list.append(float(ano_val) if ano_val is not None else 0.0)
        notas_list.append(float(nota_media_por_livro.get(l.id, 0.0)))

    anos = np.array(anos_list).reshape(-1, 1)
    notas = np.array(notas_list).reshape(-1, 1)

    scaler_ano = MinMaxScaler()
    scaler_nota = MinMaxScaler()

    anos_norm = scaler_ano.fit_transform(anos)
    notas_norm = scaler_nota.fit_transform(notas)

    vetores = {}
    ids = []

    for idx, l in enumerate(livros):
        # autor one-hot
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

        # Dar mais peso ao GÊNERO
        # Multiplicar o vetor de gênero para balancear com autor
        peso_genero = len(autores) / len(generos)  # Ex: 60/8 = 7.5
        vec_gen_ponderado = vec_gen * peso_genero

        vetor_final = np.concatenate([vec_autor, vec_gen_ponderado, [ano_val], [nota_val]])
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

def recomendar_item_based(usuario_id, bd, num_recomendacoes=6, k=7):
    """
    Recomenda livros baseado em item similarity.
    """
    vetores, ids, _ = construir_vetores_livros(bd)

    if not vetores:
        return recomendar_livros_populares(bd, num_recomendacoes)

    matriz = matriz_similaridade_itens(vetores, ids)
    id_to_index = {lid: idx for idx, lid in enumerate(ids)}

    leituras = bd.carregarLeituras(usuario_id)
    if not leituras:
        return recomendar_livros_populares(bd, num_recomendacoes)

    # ✅ CORREÇÃO: Separar em duas listas
    # 1. Livros COM avaliação → usados para calcular similaridade
    livros_avaliados = [l.id_livro for l in leituras if getattr(l, 'avaliacao', None) is not None]
    livros_avaliados = [lid for lid in livros_avaliados if lid in vetores]

    # 2. TODOS os livros lidos → usados para EXCLUIR das recomendações
    todos_livros_lidos = set(l.id_livro for l in leituras)

    if not livros_avaliados:
        # Se não tem avaliações, recomenda populares (excluindo os já lidos)
        populares = recomendar_livros_populares(bd, num_recomendacoes + len(todos_livros_lidos))
        return [p for p in populares if p not in todos_livros_lidos][:num_recomendacoes]

    score_acumulado = defaultdict(float)

    for lid in livros_avaliados:
        if lid not in id_to_index:
            continue

        idx = id_to_index[lid]
        similares = list(enumerate(matriz[idx]))
        similares = sorted(similares, key=lambda x: x[1], reverse=True)

        for i, sim in similares[1:k + 1]:
            outro = ids[i]
            # ✅ CORREÇÃO: Excluir TODOS os livros já lidos (não só os avaliados)
            if outro not in todos_livros_lidos:
                score_acumulado[outro] += sim

    ordenados = sorted(score_acumulado.items(), key=lambda x: x[1], reverse=True)
    recomendados = [lid for lid, _ in ordenados[:num_recomendacoes]]

    # Completar com populares se necessário
    if len(recomendados) < num_recomendacoes:
        populares = recomendar_livros_populares(bd, num_recomendacoes + len(todos_livros_lidos))
        for p in populares:
            # ✅ CORREÇÃO: Também excluir dos populares
            if p not in recomendados and p not in todos_livros_lidos:
                recomendados.append(p)
            if len(recomendados) >= num_recomendacoes:
                break

    return recomendados[:num_recomendacoes]


def recomendar_livros_knn(usuario_id, bd, num_recomendacoes=6, n_neighbors=7):
    """Alias para recomendar_item_based"""
    return recomendar_item_based(usuario_id, bd, num_recomendacoes, n_neighbors)


# ============================================================
# 3. Fallback: livros populares
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
# 4. Métricas e avaliação
# ============================================================

def precision_at_k(recomendacoes, itens_reais, k=5):
    k = min(k, len(recomendacoes))
    if k == 0:
        return 0.0

    recomendados = set(recomendacoes[:k])
    verdadeiros = {lid for lid, nota in itens_reais}

    acertos = len(recomendados & verdadeiros)
    return acertos / k


def recomendar_item_based_com_treino(usuario_id, bd, livros_treino_ids, num_recomendacoes=6, k=3):
    """Versão para avaliação do modelo."""
    vetores, ids, _ = construir_vetores_livros(bd)

    if not vetores or not livros_treino_ids:
        return recomendar_livros_populares(bd, num_recomendacoes)

    matriz = matriz_similaridade_itens(vetores, ids)
    id_to_index = {lid: idx for idx, lid in enumerate(ids)}

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


def avaliar_modelo(bd, k=7, n_folds=5):
    """Avalia o modelo usando k-fold cross-validation."""

    usuarios_com_avaliacoes = {}
    for uid in bd.usuarios.keys():
        leituras = [
            (l.id_livro, l.avaliacao)
            for l in bd.carregarLeituras(uid)
            if l.avaliacao is not None
        ]
        if len(leituras) >= 2:
            usuarios_com_avaliacoes[uid] = leituras

    if not usuarios_com_avaliacoes:
        print("❌ Nenhum usuário com avaliações suficientes")
        return {"mean": 0, "std": 0, "scores_por_fold": []}

    print(f"\n📊 Iniciando {n_folds}-Fold Cross-Validation")
    print(f"   Usuários válidos: {len(usuarios_com_avaliacoes)}")
    print(f"   Precision@{k}\n")

    scores_por_fold = []

    for fold_idx in range(n_folds):
        print(f"{'=' * 50}")
        print(f"Fold {fold_idx + 1}/{n_folds}")
        print(f"{'=' * 50}")

        treino_fold = {}
        teste_fold = {}

        for uid, leituras in usuarios_com_avaliacoes.items():
            kf = KFold(n_splits=n_folds, shuffle=True, random_state=42 + fold_idx)
            splits = list(kf.split(leituras))

            if fold_idx < len(splits):
                train_idx, test_idx = splits[fold_idx]
                treino_fold[uid] = [leituras[i] for i in train_idx]
                teste_fold[uid] = [leituras[i] for i in test_idx]

        scores_fold = []

        for usuario_id in treino_fold.keys():
            if usuario_id not in teste_fold or not teste_fold[usuario_id]:
                continue

            livros_treino = [l[0] for l in treino_fold[usuario_id]]
            rec = recomendar_item_based_com_treino(
                usuario_id, bd, livros_treino,
                num_recomendacoes=k, k=k
            )
            score = precision_at_k(rec, teste_fold[usuario_id], k)
            scores_fold.append(score)

        if scores_fold:
            mean_fold = sum(scores_fold) / len(scores_fold)
            scores_por_fold.append(mean_fold)
            print(f"   Usuários avaliados: {len(scores_fold)}")
            print(f"   Precision@{k}: {mean_fold:.4f}\n")

    if not scores_por_fold:
        return {"mean": 0, "std": 0, "scores_por_fold": []}

    mean_score = sum(scores_por_fold) / len(scores_por_fold)
    std_score = (sum((s - mean_score) ** 2 for s in scores_por_fold) / len(scores_por_fold)) ** 0.5

    print(f"\n{'=' * 50}")
    print(f"RESULTADOS FINAIS ({n_folds}-Fold Cross-Validation)")
    print(f"{'=' * 50}")
    print(f"Precision@{k} médio: {mean_score:.4f} ± {std_score:.4f}")

    return {
        "mean": mean_score,
        "std": std_score,
        "scores_por_fold": scores_por_fold
    }