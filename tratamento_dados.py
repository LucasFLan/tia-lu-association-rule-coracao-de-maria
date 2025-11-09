import pandas as pd
import re
import unidecode


class LimpadorVestuarios:
    """
    Tratamento leve das descrições e mapeamento para categorias.
    Retorna um DataFrame com colunas: id_transacao, itens_compra (lista de categorias).
    """

    def __init__(self):
        self.termos_excluir = {
            "pimpolho","micol","kids","baby","modas","luziane","italico","minasrey","bilu",
            "mrm","dengo","flaphy","rekorte","d","vystek","ld","needfeel","mecbee","rianna",
            "mic","boys","unissex","fem","masc","juvenil","infantil","unid","cm","moda",
            "intima","confeccoes","fashion","sergio","visual","mania","dom","matheus","sg",
            "de","da","do","com","sem","para","no","na","ao","a","o","e","c","x","tag",
            "pares","cos","bojo","aberto","tradicional","algodao","elastico","cordao"
        }


        self.grupos_produtos = {
            "camisa": {"camisa","camiseta","blusa","polo","gola polo","t shirt","tshirt","t-shirt","baby look","bata","cropped","camisa manga"},
            "regata": {"regata","machao","machão"},
            "short": {"short","shorts","bermuda","mauricinho","tactel","short-saia","short saia","bermudinha"},
            "calca": {"calca","jeans","sarja","moletom","legging","leggue","legin","jogger","calça"},
            "saia": {"saia"},
            "calcinha": {"calcinha","tanga","fio dental","calcinha box"},
            "cueca": {"cueca","boxer","cuecas","cueca box"},
            "sutia": {"sutia","top","sutiã","top cropped","bojo"},
            "sunga": {"sunga","sungas"},
            "fralda_pano": {"fralda","fraldinha","cueiro"},
            "pijama": {"pijama","baby doll","camisola","pijama longo","pijama curto"},
            "meia": {"meia","meia calca","meiao","meias"},
            "body": {"body","bory","bodie"},
            "mijao": {"mijao","mijão","mijão aberto","mijao aberto"},
            "macacao": {"macacao","macaquito","macacão","jardineira","macacao curto","macacao longo"},
            "jaqueta": {"jaqueta","casaco","cardigan"},
            "vestido": {"vestido","vestidos"},
            "biquini": {"biquini","bikini","maio","maiô"},
            "toalha": {"toalha","toalhas","toalha rosto","toalha banho","toalha de rosto","toalha de banho"},
            "roupa_cama": {"lencol","lençol","jogo de cama","fronha","edredom","coberta","cobertor","manta","cobre leito","travesseiro","protetor"}
        }

    def normalizar_texto(self, texto: str) -> str:
        if not isinstance(texto, str):
            return ""
        t = unidecode.unidecode(texto.lower())
        t = re.sub(r"[^a-z0-9\s;]", " ", t)
        t = re.sub(r"\b(p|m|g|gg|xg|2g|3g|4g|5g)\b", " ", t)
        t = re.sub(r"\d+", " ", t)
        for termo in self.termos_excluir:
            t = re.sub(rf"\b{re.escape(termo)}\b", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    def identificar_categorias(self, descricao: str) -> list:
        if not isinstance(descricao, str) or not descricao.strip():
            return []
        texto = unidecode.unidecode(descricao.lower())
        encontrados = set()
        for chave, termos in self.grupos_produtos.items():
            for termo in termos:
                if termo in texto:
                    encontrados.add(chave)
                    break
        return sorted(encontrados)

    def executar(self, caminho_csv: str) -> pd.DataFrame:
        df = pd.read_csv(caminho_csv, dtype={"id_transacao": str})
        df = df.dropna(subset=["descricao_produtos"]).copy()
        df["texto_padronizado"] = df["descricao_produtos"].apply(self.normalizar_texto)
        df["itens_compra"] = df["descricao_produtos"].apply(self.identificar_categorias)
        df = df[df["itens_compra"].apply(bool)].copy()
        df["itens_compra"] = df["itens_compra"].apply(lambda x: sorted(set(x)))
        return df[["id_transacao", "itens_compra"]]