from app import create_app
from database import bd
from controllers.recommendation_knn import (
    recomendar_item_based_com_treino,
    gerar_train_test,
    precision_at_k
)

app = create_app()

with app.app_context():
    print("=" * 60)
    print("🔍 TESTE COMPLETO - MÉDIA DE TODOS OS USUÁRIOS")
    print("=" * 60)

    treino, teste = gerar_train_test(bd, test_size=0.3)
    scores = []

    print(f"\nTestando {len(treino)} usuários com k=3...\n")

    for usuario_id in treino.keys():
        if usuario_id not in teste:
            continue

        livros_treino = [l[0] for l in treino[usuario_id]]
        rec = recomendar_item_based_com_treino(usuario_id, bd, livros_treino, num_recomendacoes=5, k=15)

        livros_teste = [l[0] for l in teste[usuario_id]]
        acertos = len(set(rec) & set(livros_teste))

        # Calcular precisão sem usar precision_at_k (mais simples)
        if len(livros_teste) > 0:
            score = acertos / len(livros_teste)
        else:
            score = 0

        scores.append(score)

        print(f"👤 {usuario_id[:8]}...: {acertos}/{len(livros_teste)} acertos = {score * 100:.1f}%")

    media = sum(scores) / len(scores) if scores else 0
    print(f"\n{'=' * 60}")
    print(f"📊 MÉDIA GERAL: {media * 100:.1f}%")
    print(f"{'=' * 60}")