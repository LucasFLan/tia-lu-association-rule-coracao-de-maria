import math
from collections import Counter
import pandas as pd

from tratamento_dados import LimpadorVestuarios
from mineracao_regras import MineradorECLAT


def executar_analise_faixas(caminho_csv="vendas_dataset.csv"):
    # Pré-processamento
    limpador = LimpadorVestuarios()
    df = limpador.executar(caminho_csv)
    transacoes = df["itens_compra"].tolist()
    total_transacoes = len(transacoes)
    print(f"Transações processadas: {total_transacoes}")

    # Parâmetros do ECLAT
    suporte_min = 0.001
    confianca_min = 0.4
    lift_min = 1.1

    print(f"\nRodando ECLAT com suporte mínimo de {suporte_min*100:.2f}%...")
    minerador = MineradorECLAT(
        suporte_min=suporte_min,
        confianca_min=confianca_min,
        lift_min=lift_min
    )
    minerador.encontrar_itemsets(transacoes, max_itens=3).gerar_regras()

    # Criação das faixas de suporte
    faixas = {
        "0.1%": [],
        "0.2%": [],
        "0.3%": [],
        "0.4%": [],
        "0.5%": []
    }

    for itemset, sup in minerador.itemsets.items():
        pct = sup * 100
        if 0.10 <= pct < 0.20:
            faixas["0.1%"].append((itemset, pct))
        elif 0.20 <= pct < 0.30:
            faixas["0.2%"].append((itemset, pct))
        elif 0.30 <= pct < 0.40:
            faixas["0.3%"].append((itemset, pct))
        elif 0.40 <= pct < 0.50:
            faixas["0.4%"].append((itemset, pct))
        elif 0.50 <= pct < 0.60:
            faixas["0.5%"].append((itemset, pct))

    print("\n Distribuição de itemsets por faixas de suporte:")
    for nome, lista in faixas.items():
        print(f"  • {nome} → {len(lista)} itemsets")
    print()

    # Exibição dos itemsets em cada faixa
    for nome, lista in faixas.items():
        if not lista:
            continue
        print(f"----- Itemsets na faixa {nome} (mostrando até 10) -----")
        ordenados = sorted(lista, key=lambda x: x[1], reverse=True)
        for itemset, pct in ordenados[:10]:
            qtd = math.ceil((pct / 100) * total_transacoes)
            print(f"  - {tuple(sorted(itemset))} | suporte = {pct:.3f}% (~{qtd} transações)")
        print()


    print("Calculando frequências reais de produtos...")

    # Lê o CSV original para pegar todos os produtos brutos
    df_bruto = pd.read_csv(caminho_csv, dtype={"id_transacao": str})
    df_bruto = df_bruto.dropna(subset=["descricao_produtos"]).copy()
    df_bruto["descricao_produtos"] = df_bruto["descricao_produtos"].astype(str)

    contador = Counter()

    # Conta cada ocorrência de produto (não apenas 1 por transação)
    for linha in df_bruto["descricao_produtos"]:
        itens = [it.strip() for it in linha.split(";") if it.strip()]
        for item_texto in itens:
            categorias = limpador.identificar_categorias(item_texto)
            if categorias:
                for cat in categorias:
                    contador[cat] += 1
            else:
                token = limpador.normalizar_texto(item_texto)
                if token:
                    contador[token] += 1

    top5 = contador.most_common(5)
    print("\n🛒 Itens/categorias mais frequentes (por ocorrência):")
    for nome, qtd in top5:
        pct = (qtd / sum(contador.values())) * 100
        print(f"  - {nome}: {qtd} ocorrências ({pct:.2f}% do total)")
    print(f"\nTotal de produtos (instâncias) contabilizadas: {sum(contador.values())}\n")

        # --- Regras de Associação ---
    if not hasattr(minerador, "regras") or not minerador.regras:
        print("⚠️ Nenhuma regra de associação encontrada com os parâmetros definidos.")
    else:
        print("\n antecedente,consequente,suporte,confianca,lift")
        print("\n Com base no maior lift, regra mais forte")

        top10 = sorted(minerador.regras, key=lambda x: x["lift"], reverse=True)[:10]

        for regra in top10:
            antecedente = str(tuple(regra["antecedente"]))
            consequente = str(tuple(regra["consequente"]))
            suporte = regra["suporte"]
            confianca = regra["confianca"]
            lift = regra["lift"]

            # print no formato exato do CSV
            print(f"\"{antecedente}\",\"{consequente}\",{suporte},{confianca},{lift}")

    # Resultado final
    total_faixas = sum(len(v) for v in faixas.values())
    if total_faixas == 0:
        print(" Nenhum itemset encontrado entre 0.1% e 0.5%.")
        print("Tente reduzir o suporte mínimo (ex: 0.0005 = 0.05%).")
    else:
        print(" Análise concluída com sucesso.")


if __name__ == "__main__":
    executar_analise_faixas()
