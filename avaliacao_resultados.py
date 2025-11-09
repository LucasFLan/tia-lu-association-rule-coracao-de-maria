import pandas as pd


def gerar_insights(modelo):
    print("\n=== Resumo: Itemsets por tamanho ===")
    agrup = {}
    for conj, sup in modelo.itemsets_encontrados.items():
        k = len(conj)
        agrup.setdefault(k, []).append((conj, sup))

    for k in sorted(agrup.keys()):
        print(f"\n-- Tamanho {k} --")
        top = sorted(agrup[k], key=lambda x: x[1], reverse=True)[:10]
        for conj, sup in top:
            print(f"  {' + '.join(sorted(conj))}  |  {sup:.2%}")

    if modelo.regras_associacao:
        print("\n=== Top Regras ===")
        for i, r in enumerate(modelo.regras_associacao[:10], 1):
            ant = ' + '.join(r['antecedente'])
            cons = ' + '.join(r['consequente'])
            print(f"{i}. [{ant}] -> [{cons}]  sup={r['suporte']:.2%} conf={r['confianca']:.1%} lift={r['lift']:.2f}")
    else:
        print("\nNenhuma regra gerada.")


def sugerir_combos(modelo):
    exemplos = [["camisa"], ["calcinha"], ["short", "camisa"], ["pijama"]]
    print("\n=== Exemplos de recomendações ===")
    for c in exemplos:
        recs = modelo.sugerir_combos(c, limite=5)
        print(f"\nCarrinho: {c}")
        if recs:
            for i, (item, score) in enumerate(recs, 1):
                print(f"  {i}. {item} (score: {score:.2f})")
        else:
            print("  Sem recomendações")