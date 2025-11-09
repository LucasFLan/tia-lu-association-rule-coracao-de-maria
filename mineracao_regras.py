
import math
from itertools import combinations
from collections import defaultdict
import pandas as pd


class MineradorECLAT:
    """
    Classe que implementa o algoritmo ECLAT e gera regras de associação.
    Guarda os itemsets e suas métricas básicas.
    """

    def __init__(self, suporte_min=0.01, confianca_min=0.4, lift_min=1.1):
        self.suporte_min = suporte_min
        self.confianca_min = confianca_min
        self.lift_min = lift_min
        self.transacoes = []
        self.total_transacoes = 0
        self.itemsets = {}         
        self.regras = []           


    def _gerar_tidlist(self, transacoes):
        tid_map = defaultdict(set)
        for idx, itens in enumerate(transacoes):
            for item in itens:
                tid_map[item].add(idx)
        return {k: frozenset(v) for k, v in tid_map.items()}

    def _explorar_combinacoes(self, tid_dict, min_ocorrencias):
        iniciais = [(frozenset([i]), t) for i, t in tid_dict.items() if len(t) >= min_ocorrencias]
        iniciais.sort(key=lambda x: len(x[1]))
        resultados = {}

        def expandir(prefixo, restantes):
            ordenados = sorted(restantes.items(), key=lambda x: len(x[1]))
            for i, (item, tids_item) in enumerate(ordenados):
                novo_itemset = prefixo | item
                suporte = len(tids_item) / self.total_transacoes
                if suporte >= self.suporte_min:
                    resultados[novo_itemset] = suporte
                futuros = {}
                for prox_item, prox_tids in ordenados[i + 1:]:
                    inter = tids_item & prox_tids
                    if len(inter) >= min_ocorrencias:
                        futuros[prox_item] = inter
                if futuros:
                    expandir(novo_itemset, futuros)

        expandir(frozenset(), dict(iniciais))
        return resultados

    # -----------------------------
    # Função principal para minerar
    # -----------------------------
    def encontrar_itemsets(self, transacoes, max_itens=None):
        self.transacoes = [sorted(set(t)) for t in transacoes if t]
        self.total_transacoes = len(self.transacoes)

        min_ocorrencias = max(1, math.ceil(self.suporte_min * self.total_transacoes))
        tid_dict = self._gerar_tidlist(self.transacoes)
        combinacoes = self._explorar_combinacoes(tid_dict, min_ocorrencias)

        if max_itens:
            combinacoes = {c: s for c, s in combinacoes.items() if len(c) <= max_itens}

        self.itemsets = combinacoes
        return self

    # -----------------------------
    # regras de associação
    # -----------------------------
    def gerar_regras(self):
        regras_encontradas = []
        for conjunto, sup_conjunto in self.itemsets.items():
            if len(conjunto) < 2:
                continue
            itens = list(conjunto)
            for r in range(1, len(itens)):
                for ant in combinations(itens, r):
                    ant_set = frozenset(ant)
                    cons_set = conjunto - ant_set
                    sup_ant = self.itemsets.get(ant_set, 0)
                    sup_cons = self.itemsets.get(cons_set, 0)
                    if not sup_ant or not sup_cons:
                        continue
                    confianca = sup_conjunto / sup_ant
                    lift = confianca / sup_cons
                    if confianca >= self.confianca_min and lift >= self.lift_min:
                        regras_encontradas.append({
                            "antecedente": tuple(sorted(ant_set)),
                            "consequente": tuple(sorted(cons_set)),
                            "suporte": sup_conjunto,
                            "confianca": confianca,
                            "lift": lift
                        })

        regras_encontradas.sort(key=lambda x: (-x["lift"], -x["confianca"], -x["suporte"]))
        self.regras = regras_encontradas
        return self

    # -----------------------------
    # regras em DataFrame
    # -----------------------------
    def exportar_regras(self):
        return pd.DataFrame(self.regras) if self.regras else pd.DataFrame()

    # -----------------------------
    # Sugestão de combinações 
    # -----------------------------
    def recomendar_itens(self, carrinho, limite=5):
        base = set(carrinho)
        ranking = defaultdict(float)
        for r in self.regras:
            antecedente = set(r["antecedente"])
            if antecedente.issubset(base):
                for c in r["consequente"]:
                    if c not in base:
                        ranking[c] += r["lift"] * r["confianca"]
        return sorted(ranking.items(), key=lambda x: x[1], reverse=True)[:limite]
