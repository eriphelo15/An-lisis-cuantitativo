from dataclasses import dataclass


@dataclass(frozen=True)
class ModeloCostos:
    """Costo conservador de un trade completo (entrada + salida) en small caps, como fracción del precio.

    Sin datos de bid/ask históricos, el spread se estima por tramo de precio y se castiga la iliquidez.
    Los valores son deliberadamente pesimistas: un edge que sobrevive a estos costos es más creíble.
    """

    tramos_spread: tuple[tuple[float, float], ...] = (
        (2.0, 0.015),
        (5.0, 0.008),
        (10.0, 0.005),
        (float("inf"), 0.003),
    )
    dolar_volumen_iliquido: float = 1_000_000
    recargo_iliquidez: float = 1.5
    slippage_por_lado: float = 0.001
    comision_por_lado: float = 0.0

    def spread(self, precio: float) -> float:
        return next(s for limite, s in self.tramos_spread if precio < limite)

    def costo_ida_vuelta(self, precio: float, dolar_volumen: float) -> float:
        spread = self.spread(precio)
        if dolar_volumen < self.dolar_volumen_iliquido:
            spread *= self.recargo_iliquidez
        return spread + 2 * (self.slippage_por_lado + self.comision_por_lado)
