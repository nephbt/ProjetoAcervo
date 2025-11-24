from app import create_app
from database import bd
from controllers.recommendation_knn import (
    recomendar_item_based_com_treino,
    construir_vetores_livros,
    gerar_train_test
)
from collections import defaultdict

app = create_app()

with app.app_context():
    print("=" * 60)
    print("🔍 DEBUG DO SISTEMA DE RECOMENDAÇÃO")
    print("=" * 60)

    # 1. Verificar dados brutos
    print("\n1️⃣ DADOS BRUTOS NO BANCO:")
    print(f"   Total de usuários: {len(bd.usuarios)}")
    print(f"   Total de livros: {len(bd.livros)}")

    # 2. Verificar leituras por usuário
    print("\n2️⃣ LEITURAS POR USUÁRIO:")
    total_leituras = 0
    usuarios_com_avaliacoes = 0

    for uid in bd.usuarios.keys():
        leituras = bd.carregarLeituras(uid) or []
        avaliadas = [l for l in leituras if getattr(l, 'avaliacao', None) is not None]
        total_leituras += len(avaliadas)
        if len(avaliadas) > 0:
            usuarios_com_avaliacoes += 1
        print(f"   Usuário {uid[:8]}...: {len(leituras)} leituras, {len(avaliadas)} com avaliação")

    print(f"\n   ✓ Total de leituras: {total_leituras}")
    print(f"   ✓ Usuários com avaliações: {usuarios_com_avaliacoes}")

    # 3. Verificar vetores de livros
    print("\n3️⃣ CONSTRUÇÃO DE VETORES:")
    vetores, ids, livros = construir_vetores_livros(bd)
    print(f"   ✓ Livros vetorizados: {len(vetores)}")
    print(f"   ✓ Dimensão do vetor: {len(vetores[ids[0]]) if ids else 0}")

    # 4. Verificar split treino/teste
    print("\n4️⃣ SPLIT TREINO/TESTE:")
    treino, teste = gerar_train_test(bd, test_size=0.3)
    print(f"   ✓ Usuários no treino: {len(treino)}")
    print(f"   ✓ Usuários no teste: {len(teste)}")

    for uid in teste.keys():
        train_count = len(treino.get(uid, []))
        test_count = len(teste[uid])
        print(f"   - {uid[:8]}...: {train_count} treino, {test_count} teste")

    # 5. Testar recomendação para um usuário específico
    print("\n5️⃣ TESTE DE RECOMENDAÇÃO:")
    if treino:
        uid_teste = list(treino.keys())[0]
        print(f"   Testando para usuário: {uid_teste[:8]}...")

        # ✅ Usar a nova função com livros de treino
        livros_treino = [l[0] for l in treino[uid_teste]]
        rec = recomendar_item_based_com_treino(uid_teste, bd, livros_treino, num_recomendacoes=5, k=3)
        print(f"   ✓ Recomendações retornadas: {rec}")

        # Verificar o que foi recomendado vs o que deveria ter sido
        print(f"   ✓ Livros lidos (treino): {livros_treino}")

        teste_real = [l[0] for l in teste[uid_teste]]
        print(f"   ✓ Livros para teste: {teste_real}")

        acertos = set(rec) & set(teste_real)
        print(f"   ✓ Acertos: {len(acertos)}/{len(teste_real)} = {len(acertos) / len(teste_real) * 100:.1f}%")

    print("\n" + "=" * 60)