from app import create_app
from database import bd
from controllers.recommendation_knn import recomendar_item_based_com_treino, gerar_train_test
from collections import defaultdict

app = create_app()

with app.app_context():
    print("=" * 80)
    print("🔍 TESTANDO DIFERENTES VALORES DE K")
    print("=" * 80)

    treino, teste = gerar_train_test(bd, test_size=0.3)

    # Testar vários valores de k
    k_values = [3, 5, 10, 15, 20]

    for k in k_values:
        scores = []

        for usuario_id in treino.keys():
            if usuario_id not in teste:
                continue

            # ✅ Usar livros de treino apenas
            livros_treino = [l[0] for l in treino[usuario_id]]
            rec = recomendar_item_based_com_treino(usuario_id, bd, livros_treino, num_recomendacoes=5, k=k)

            livros_teste = [l[0] for l in teste[usuario_id]]
            acertos = len(set(rec) & set(livros_teste))

            if livros_teste:
                score = acertos / len(livros_teste)
                scores.append(score)

        media = sum(scores) / len(scores) if scores else 0
        print(f"\n🎯 k={k:2d}: Precisão média = {media:.1%} ({len(scores)} usuários)")
        for i, s in enumerate(scores, 1):
            print(f"     Usuário {i}: {s:.1%}")

    print("\n" + "=" * 80)