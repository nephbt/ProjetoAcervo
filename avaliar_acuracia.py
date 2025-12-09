"""
Avaliação do Sistema de Recomendação
- LOOCV (Leave-One-Out Cross-Validation)
- Teste de diferentes valores de K
- Demonstração visual das recomendações
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collections import defaultdict
import numpy as np
from ia.db_adapter import bd_adapter
from ia.recommendation_knn import (
    construir_vetores_livros,
    matriz_similaridade_itens,
    recomendar_livros_populares
)


# ============================================================
# 1. FUNÇÕES AUXILIARES
# ============================================================

def recomendar_com_k(usuario_id, bd, livros_treino, num_recomendacoes=5, k=10):
    """
    Recomenda livros usando apenas os livros de treino.
    Permite testar diferentes valores de K.
    """
    vetores, ids, _ = construir_vetores_livros(bd)

    if not vetores or not livros_treino:
        return []

    matriz = matriz_similaridade_itens(vetores, ids)
    id_to_index = {lid: idx for idx, lid in enumerate(ids)}

    score_acumulado = defaultdict(float)

    for lid in livros_treino:
        if lid not in id_to_index:
            continue

        idx = id_to_index[lid]
        similares = list(enumerate(matriz[idx]))
        similares = sorted(similares, key=lambda x: x[1], reverse=True)

        for i, sim in similares[1:k + 1]:
            outro = ids[i]
            if outro not in livros_treino:
                score_acumulado[outro] += sim

    ordenados = sorted(score_acumulado.items(), key=lambda x: x[1], reverse=True)
    return [lid for lid, _ in ordenados[:num_recomendacoes]]


# ============================================================
# 2. LOOCV - Leave-One-Out Cross-Validation
# ============================================================

def avaliar_loocv(bd, k=10, num_recomendacoes=5):
    """
    Avaliação com Leave-One-Out:
    Para cada usuário, esconde 1 livro por vez e tenta prever.
    """
    print(f"\n{'='*60}")
    print(f"📊 LOOCV - Leave-One-Out (K={k})")
    print(f"{'='*60}")

    hits = 0
    total = 0
    posicoes = []

    for uid in bd.usuarios.keys():
        leituras = bd.carregarLeituras(uid)
        livros_avaliados = [l.id_livro for l in leituras if l.avaliacao is not None]

        if len(livros_avaliados) < 3:  # Precisa de pelo menos 3 para fazer sentido
            continue

        # Para cada livro, esconde ele e tenta prever
        for livro_teste in livros_avaliados:
            livros_treino = [l for l in livros_avaliados if l != livro_teste]

            recomendacoes = recomendar_com_k(uid, bd, livros_treino, num_recomendacoes, k)

            total += 1

            if livro_teste in recomendacoes:
                hits += 1
                posicao = recomendacoes.index(livro_teste) + 1
                posicoes.append(posicao)

    hit_rate = hits / total if total > 0 else 0
    mrr = sum(1/p for p in posicoes) / total if total > 0 else 0

    print(f"   Total de testes: {total}")
    print(f"   Acertos: {hits}")
    print(f"   Hit Rate: {hit_rate:.1%}")
    print(f"   MRR: {mrr:.4f}")

    return {
        "k": k,
        "total": total,
        "hits": hits,
        "hit_rate": hit_rate,
        "mrr": mrr
    }


# ============================================================
# 3. TESTE DE DIFERENTES VALORES DE K
# ============================================================

def testar_valores_k(bd, valores_k=[3, 5, 7, 10, 15, 20], num_recomendacoes=5):
    """
    Testa diferentes valores de K e mostra qual é o melhor.
    """
    print(f"\n{'='*60}")
    print("🔬 TESTE DE DIFERENTES VALORES DE K")
    print(f"{'='*60}")

    resultados = []

    for k in valores_k:
        resultado = avaliar_loocv(bd, k=k, num_recomendacoes=num_recomendacoes)
        resultados.append(resultado)

    # Encontrar o melhor K
    melhor = max(resultados, key=lambda x: x["hit_rate"])

    print(f"\n{'='*60}")
    print("📊 COMPARAÇÃO DE VALORES DE K")
    print(f"{'='*60}")
    print(f"{'K':<6} {'Hit Rate':<12} {'MRR':<10} {'Acertos':<10}")
    print("-" * 40)

    for r in resultados:
        marcador = " ⭐" if r["k"] == melhor["k"] else ""
        print(f"{r['k']:<6} {r['hit_rate']:<12.1%} {r['mrr']:<10.4f} {r['hits']}/{r['total']}{marcador}")

    print(f"\n✅ MELHOR K = {melhor['k']} (Hit Rate: {melhor['hit_rate']:.1%})")

    return resultados, melhor


# ============================================================
# 4. DEMONSTRAÇÃO VISUAL DAS RECOMENDAÇÕES
# ============================================================

def demonstrar_recomendacoes(bd, num_usuarios=5, k=10):
    """
    Mostra exemplos reais de recomendações para usuários.
    """
    print(f"\n{'='*60}")
    print("🎯 DEMONSTRAÇÃO DE RECOMENDAÇÕES")
    print(f"{'='*60}")

    usuarios_validos = []
    for uid in bd.usuarios.keys():
        leituras = bd.carregarLeituras(uid)
        livros_avaliados = [(l.id_livro, l.avaliacao) for l in leituras if l.avaliacao is not None]
        if len(livros_avaliados) >= 3:
            usuarios_validos.append((uid, livros_avaliados))

    # Pegar alguns usuários de exemplo
    for uid, leituras in usuarios_validos[:num_usuarios]:
        print(f"\n{'─'*60}")
        print(f"👤 Usuário: {uid[:8]}...")

        # Mostrar o que ele leu
        print(f"\n📚 Livros lidos ({len(leituras)}):")
        generos_lidos = defaultdict(int)

        for livro_id, nota in leituras[:5]:  # Mostrar até 5
            livro = bd.buscarLivroPorId(livro_id)
            if livro:
                print(f"   • {livro.titulo} ({livro.genero}) - Nota: {nota}")
                generos_lidos[livro.genero] += 1

        if len(leituras) > 5:
            print(f"   ... e mais {len(leituras) - 5} livros")

        # Gênero favorito
        genero_fav = max(generos_lidos, key=generos_lidos.get) if generos_lidos else "N/A"
        print(f"\n❤️ Gênero favorito: {genero_fav}")

        # Gerar recomendações
        livros_ids = [l[0] for l in leituras]
        recomendacoes = recomendar_com_k(uid, bd, livros_ids, num_recomendacoes=6, k=k)

        print(f"\n🎯 Recomendações:")
        acertos_genero = 0

        for i, rec_id in enumerate(recomendacoes, 1):
            livro = bd.buscarLivroPorId(rec_id)
            if livro:
                match = "✅" if livro.genero == genero_fav else "  "
                if livro.genero in generos_lidos:
                    acertos_genero += 1
                print(f"   {i}. {livro.titulo} ({livro.genero}) {match}")

        precisao_genero = acertos_genero / len(recomendacoes) if recomendacoes else 0
        print(f"\n📊 Precisão por gênero: {precisao_genero:.0%} ({acertos_genero}/{len(recomendacoes)} do gênero que ele gosta)")


# ============================================================
# 5. ANÁLISE DE SIMILARIDADE
# ============================================================

def analisar_similaridade(bd):
    """
    Analisa a similaridade entre livros para entender o modelo.
    """
    print(f"\n{'='*60}")
    print("🔍 ANÁLISE DE SIMILARIDADE ENTRE LIVROS")
    print(f"{'='*60}")

    vetores, ids, livros = construir_vetores_livros(bd)

    if not vetores:
        print("❌ Sem dados para análise")
        return

    matriz = matriz_similaridade_itens(vetores, ids)

    # Para cada gênero, mostrar livros mais similares
    generos = defaultdict(list)
    for livro in livros:
        generos[livro.genero].append(livro)

    print(f"\n📚 Gêneros no catálogo: {len(generos)}")
    for genero, livros_genero in sorted(generos.items(), key=lambda x: -len(x[1])):
        print(f"   • {genero}: {len(livros_genero)} livros")

    # Pegar um livro exemplo de cada gênero principal
    print(f"\n🔗 Exemplos de similaridade:")

    id_to_index = {lid: idx for idx, lid in enumerate(ids)}

    for genero in list(generos.keys())[:3]:  # Top 3 gêneros
        livro_exemplo = generos[genero][0]

        if livro_exemplo.id not in id_to_index:
            continue

        idx = id_to_index[livro_exemplo.id]
        similares = list(enumerate(matriz[idx]))
        similares = sorted(similares, key=lambda x: x[1], reverse=True)

        print(f"\n   📖 '{livro_exemplo.titulo}' ({genero})")
        print(f"   Livros mais similares:")

        for i, sim in similares[1:4]:  # Top 3 similares
            outro = bd.buscarLivroPorId(ids[i])
            if outro:
                match = "✅" if outro.genero == genero else "❌"
                print(f"      {match} {outro.titulo} ({outro.genero}) - sim: {sim:.2f}")


# ============================================================
# 6. MAIN
# ============================================================

def main():
    print("="*60)
    print("📊 AVALIAÇÃO COMPLETA DO SISTEMA DE RECOMENDAÇÃO")
    print("="*60)

    bd = bd_adapter
    bd.invalidar_cache()  # Garante dados frescos

    # Estatísticas básicas
    stats = bd.obter_estatisticas()
    print(f"\n📌 Base de dados:")
    print(f"   • Livros: {stats['total_livros']}")
    print(f"   • Usuários: {stats['total_usuarios']}")
    print(f"   • Avaliações: {stats['total_avaliacoes']}")

    # 1. Testar diferentes valores de K
    resultados_k, melhor_k = testar_valores_k(
        bd,
        valores_k=[3, 5, 7, 10, 15, 20],
        num_recomendacoes=5
    )

    # 2. Demonstração visual com o melhor K
    demonstrar_recomendacoes(bd, num_usuarios=3, k=melhor_k["k"])

    # 3. Análise de similaridade
    analisar_similaridade(bd)

    # Resumo final
    print(f"\n{'='*60}")
    print("🏆 RESUMO FINAL")
    print(f"{'='*60}")
    print(f"✅ Melhor valor de K: {melhor_k['k']}")
    print(f"✅ Hit Rate com LOOCV: {melhor_k['hit_rate']:.1%}")
    print(f"✅ MRR: {melhor_k['mrr']:.4f}")
    print(f"\n💡 Recomendação: Altere k=15 para k={melhor_k['k']} no recommendation_knn.py")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
