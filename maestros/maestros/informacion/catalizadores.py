import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


@dataclass(frozen=True)
class Noticia:
    id: str
    tickers: tuple[str, ...]
    hora: datetime
    titular: str
    resumen: str
    fuente: str
    url: str

    @property
    def texto(self) -> str:
        return f"{self.titular}. {self.resumen}"


class TipoCatalizador(StrEnum):
    OFERTA = "oferta"
    REVERSE_SPLIT = "reverse_split"
    FUSION = "fusion_adquisicion"
    FDA = "fda"
    ENSAYO = "ensayo_clinico"
    RESULTADOS = "resultados"
    CONTRATO = "contrato"
    ALIANZA = "alianza"
    TEMATICO = "tematico"
    LISTADO = "listado"
    OTRO = "otro"


# El orden importa: una oferta o un reverse split se detectan antes que cualquier noticia "positiva".
REGLAS_TIPO: tuple[tuple[TipoCatalizador, re.Pattern], ...] = tuple(
    (tipo, re.compile(patron, re.IGNORECASE))
    for tipo, patron in (
        (TipoCatalizador.OFERTA, r"\bpric(e|es|ed|ing)\b.{0,60}\b(offering|placement)\b|\bregistered direct\b"
                                 r"|\bpublic offering\b|\bprivate placement\b|\bat[- ]the[- ]market\b"
                                 r"|\bwarrant (exercise|inducement)\b"),
        (TipoCatalizador.REVERSE_SPLIT, r"\breverse (stock )?split\b"),
        (TipoCatalizador.FUSION, r"\bmerger\b|\bacquisition\b|\bto acquire\b|\bto be acquired\b|\bbusiness combination\b"),
        (TipoCatalizador.FDA, r"\bFDA\b|\b510\(k\)|\bfast track\b|\borphan drug\b|\bbreakthrough therapy\b"),
        (TipoCatalizador.ENSAYO, r"\bphase (1|2|3|i{1,3})\b|\bclinical trial\b|\btopline\b|\btrial results\b"),
        (TipoCatalizador.RESULTADOS, r"\b(quarter|quarterly|fiscal|full[- ]year)\b.{0,40}\bresults\b|\bearnings\b"
                                     r"|\brevenue (growth|increase)\b|\braises guidance\b"),
        (TipoCatalizador.CONTRATO, r"\bcontract\b|\bpurchase order\b|\bawarded\b|\bsupply agreement\b"),
        (TipoCatalizador.ALIANZA, r"\bpartnership\b|\bpartners with\b|\bcollaboration\b|\bjoint venture\b"
                                  r"|\bletter of intent\b|\bmemorandum of understanding\b|\bagreement with\b"),
        (TipoCatalizador.TEMATICO, r"\bbitcoin\b|\bcrypto\b|\bblockchain\b|\bartificial intelligence\b|\bAI\b|\bquantum\b"),
        (TipoCatalizador.LISTADO, r"\buplist(ing)?\b|\bregains? compliance\b"),
    )
)

BASE_POR_TIPO = {
    TipoCatalizador.FDA: 70, TipoCatalizador.FUSION: 70, TipoCatalizador.ENSAYO: 60,
    TipoCatalizador.CONTRATO: 55, TipoCatalizador.RESULTADOS: 50, TipoCatalizador.ALIANZA: 40,
    TipoCatalizador.TEMATICO: 35, TipoCatalizador.LISTADO: 30, TipoCatalizador.OTRO: 20,
    TipoCatalizador.OFERTA: 0, TipoCatalizador.REVERSE_SPLIT: 0,
}
TIPOS_NEGATIVOS = {TipoCatalizador.OFERTA, TipoCatalizador.REVERSE_SPLIT}

MONTO = re.compile(r"\$\s?(\d+(?:[.,]\d+)?)\s*(billion|million|bn|mm|m|b)\b", re.IGNORECASE)
NO_VINCULANTE = re.compile(r"\bletter of intent\b|\bmemorandum of understanding\b|\bMOU\b|\bnon-binding\b", re.IGNORECASE)
VINCULANTE = re.compile(r"\bdefinitive agreement\b|\bsigned\b", re.IGNORECASE)
PROMOCIONAL = re.compile(r"\b(revolutionary|game[- ]chang\w*|transformational|unprecedented|groundbreaking|disruptive"
                         r"|paradigm|explosive|massive)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Catalizador:
    noticia: Noticia
    tipo: TipoCatalizador
    puntaje: int
    razones: tuple[str, ...]


def clasificar_tipo(noticia: Noticia) -> TipoCatalizador:
    for tipo, patron in REGLAS_TIPO:
        if patron.search(noticia.texto):
            return tipo
    return TipoCatalizador.OTRO


def monto_mayor(texto: str) -> float | None:
    montos = []
    for numero, unidad in MONTO.findall(texto):
        valor = float(numero.replace(",", ""))
        montos.append(valor * (1e9 if unidad.lower() in ("billion", "bn", "b") else 1e6))
    return max(montos) if montos else None


def evaluar_catalizador(noticia: Noticia, capitalizacion: float | None = None,
                        dilucion_alta: bool = False) -> Catalizador:
    """Puntaje 0-100 con reglas explícitas. El backtest decide después si el puntaje predice algo."""
    tipo = clasificar_tipo(noticia)
    puntaje = BASE_POR_TIPO[tipo]
    razones = [f"tipo {tipo.value} ({puntaje})"]
    if tipo not in TIPOS_NEGATIVOS:
        monto = monto_mayor(noticia.texto)
        if monto and capitalizacion:
            proporcion = monto / capitalizacion
            ajuste = 20 if proporcion >= 0.5 else 10 if proporcion >= 0.1 else -10 if proporcion < 0.02 else 0
            if ajuste:
                puntaje += ajuste
                razones.append(f"monto {proporcion:.0%} de la capitalización ({ajuste:+d})")
        if NO_VINCULANTE.search(noticia.texto):
            puntaje -= 15
            razones.append("acuerdo no vinculante (-15)")
        elif VINCULANTE.search(noticia.texto):
            puntaje += 5
            razones.append("acuerdo definitivo (+5)")
        if len(PROMOCIONAL.findall(noticia.texto)) >= 2:
            puntaje -= 10
            razones.append("lenguaje promocional (-10)")
        if dilucion_alta:
            puntaje -= 15
            razones.append("dilución pendiente alta (-15)")
    return Catalizador(noticia, tipo, max(0, min(100, puntaje)), tuple(razones))
