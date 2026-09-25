"""Algoritmo basado en el método público de Ross Cameron (Warrior Trading). Versión literal.

Solo long, intradía, en velas de 1 minuto. Las reglas de selección y de trade vienen de su material
público; los parámetros marcados como "de implementación" no los define la fuente y el backtest los pone
a prueba.
"""

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from maestros.backtest.modelos import Direccion, Senal
from maestros.datos.calendario import APERTURA, CIERRE, dias_habiles_previos, en_et
from maestros.traders.base import Contexto
from maestros.traders.indicadores import volumen_relativo, vwap

TICK = 0.01

FUENTES = {
    "pilares": "Warrior Trading, 'Stock Selection' (PDF) y los 5 pilares: precio, alza del día, volumen "
               "relativo, catalizador de noticias y float bajo",
    "horario": "Warrior Trading: la ventana principal de momentum es el premarket y la primera hora y media",
    "setups": "Warrior Trading (artículos y recaps): micro pullback, bull flag y gap and go; entrada en la "
              "primera vela que hace un nuevo máximo, stop en el mínimo del pullback",
    "objetivo": "Warrior Trading: relación ganancia/pérdida de 2 a 1",
}


@dataclass(frozen=True)
class ParametrosCameron:
    # Pilares (fuente: "pilares")
    precio_min: float = 1.0
    precio_max: float = 20.0
    alza_min: float = 0.10
    volumen_relativo_min: float = 5.0
    float_max: float = 20_000_000
    exigir_catalizador: bool = True
    # Horario (fuente: "horario")
    hora_inicio: time = time(7, 0)
    hora_fin: time = time(11, 0)
    # Objetivo (fuente: "objetivo")
    relacion_objetivo: float = 2.0
    # De implementación
    impulso_min: float = 0.05
    velas_impulso: int = 10
    max_velas_micro: int = 2
    min_velas_bandera: int = 3
    max_velas_bandera: int = 6
    retroceso_max: float = 0.5
    minutos_gap_and_go: int = 5
    distancia_max_gap_and_go: float = 0.03
    riesgo_max_pct: float = 0.10


class CameronLiteral:
    nombre = "cameron_literal"

    def __init__(self, params: ParametrosCameron = ParametrosCameron()):
        self.p = params

    def revisar_pilares(self, ctx: Contexto) -> str | None:
        """Devuelve el primer pilar que falla, o None si se cumplen los cinco."""
        precio = float(ctx.barras["cierre"].iloc[-1])
        if not self.p.precio_min <= precio <= self.p.precio_max:
            return "precio"
        if precio / ctx.cierre_previo - 1 < self.p.alza_min:
            return "alza"
        relativo = volumen_relativo(ctx.barras, ctx.volumen_normal)
        if relativo is None or relativo < self.p.volumen_relativo_min:
            return "volumen_relativo"
        if ctx.ficha is None or ctx.ficha.float_aprox is None or ctx.ficha.float_aprox > self.p.float_max:
            return "float"
        if self.p.exigir_catalizador:
            desde = en_et(dias_habiles_previos(ctx.fecha, 1)[0], CIERRE)
            if not ctx.ficha.noticias_entre(desde, ctx.ahora):
                return "catalizador"
        return None

    def evaluar(self, ctx: Contexto) -> Senal | None:
        if not self.p.hora_inicio <= ctx.ahora.time() < self.p.hora_fin:
            return None
        if self.revisar_pilares(ctx) is not None:
            return None
        return self._gap_and_go(ctx) or self._pullback(ctx, "bull_flag") or self._pullback(ctx, "micro_pullback")

    def _senal(self, setup: str, entrada: float, stop: float, ahora: datetime, motivo: str) -> Senal | None:
        entrada, stop = round(entrada, 4), round(stop, 4)
        if entrada <= stop or (entrada - stop) / entrada > self.p.riesgo_max_pct:
            return None
        objetivo = round(entrada + self.p.relacion_objetivo * (entrada - stop), 4)
        return Senal(setup, Direccion.LARGO, entrada, stop, objetivo, ahora, motivo)

    def _gap_and_go(self, ctx: Contexto) -> Senal | None:
        ahora = ctx.ahora
        apertura = en_et(ctx.fecha, APERTURA)
        if not apertura <= ahora < apertura + timedelta(minutes=self.p.minutos_gap_and_go):
            return None
        b = ctx.barras
        premercado = b[b["hora"] < apertura]
        sesion = b[b["hora"] >= apertura]
        if premercado.empty or sesion.empty:
            return None
        maximo_pm = float(premercado["maximo"].max())
        if float(sesion["apertura"].iloc[0]) / ctx.cierre_previo - 1 < self.p.alza_min:
            return None
        if float(sesion["maximo"].max()) > maximo_pm:
            return None  # ya rompió el máximo del premarket: la entrada de ruptura pasó
        precio = float(b["cierre"].iloc[-1])
        if precio < maximo_pm * (1 - self.p.distancia_max_gap_and_go):
            return None
        return self._senal("gap_and_go", maximo_pm + TICK, float(sesion["minimo"].min()) - TICK, ahora,
                           f"ruptura del máximo del premarket {maximo_pm:.2f}")

    def _pullback(self, ctx: Contexto, setup: str) -> Senal | None:
        b = ctx.barras.reset_index(drop=True)
        if setup == "bull_flag":
            rango = range(self.p.min_velas_bandera, self.p.max_velas_bandera + 1)
        else:
            rango = range(1, self.p.max_velas_micro + 1)
        if float(b["cierre"].iloc[-1]) <= float(vwap(b).iloc[-1]):
            return None

        for k in rango:
            if len(b) < k + self.p.velas_impulso:
                return None
            retroceso, previas = b.iloc[-k:], b.iloc[:-k]
            tramo = previas.iloc[-self.p.velas_impulso:]
            techo = float(tramo["maximo"].iloc[-1])
            if techo < float(tramo["maximo"].max()) or float(retroceso["maximo"].max()) >= techo:
                continue  # el impulso debe terminar justo antes del retroceso y este no puede superar el techo
            idx_piso = tramo["minimo"].idxmin()
            piso = float(tramo["minimo"].min())
            minimo_retroceso = float(retroceso["minimo"].min())
            if techo / piso - 1 < self.p.impulso_min:
                continue
            if (techo - minimo_retroceso) / (techo - piso) > self.p.retroceso_max:
                continue
            if setup == "bull_flag":
                mastil = b.loc[idx_piso: previas.index[-1]]
                if float(retroceso["volumen"].mean()) >= float(mastil["volumen"].mean()):
                    continue  # la bandera debe consolidar con menos volumen que el mástil
            return self._senal(setup, float(retroceso["maximo"].iloc[-1]) + TICK, minimo_retroceso - TICK,
                               ctx.ahora, f"retroceso de {k} velas tras impulso de {techo / piso - 1:.0%}")
        return None
