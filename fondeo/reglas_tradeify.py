"""Reglas Tradeify (verificadas 2026-09-26).

Fuentes:
  * OFICIAL: datos de planes embebidos en https://tradeify.co (GrowthData / SelectData / LightningData):
    objetivo, drawdown EOD, DLL, contratos, consistencia de examen, precio lista, reinicio.
  * SECUNDARIAS (el centro de ayuda bloquea acceso automático): propdatalab.com (26-ago-2026),
    tradetanto.com (25-jun-2026), fundedprogramfinder.com (31-mar-2026). Coinciden en lo esencial:
    lock del drawdown, días rentables, saldo mínimo, split 90/10, prohibiciones.
  * Donde difieren, se usa el valor OFICIAL; lo marcado CONFIRMAR debe verificarse en el panel antes de comprar.

Todo en USD. Drawdown EOD trailing: el piso = máximo saldo de CIERRE − DD, aplicado en tiempo real
(si el equity intradía toca el piso, la cuenta se pierde). Se congela en inicio + 100 cuando el saldo EOD
supera inicio + DD + 100.
"""
PRECIO_LISTA = {  # examen / Lightning (pago único)
    ("growth", 25): 99, ("growth", 50): 145, ("growth", 100): 255, ("growth", 150): 369,
    ("select", 25): 109, ("select", 50): 165, ("select", 100): 265, ("select", 150): 369,
    ("lightning", 25): 345, ("lightning", 50): 492, ("lightning", 100): 660, ("lightning", 150): 796,
}
DESCUENTO_TIPICO = 0.30   # cupones recurrentes 30-40% (40% máx 5 usos). CONFIRMAR al comprar.

EXAMEN = {
    "growth": {25: dict(target=1500, dd=1000, dll=600, consist=None, min_dias=1, max_mini=1),
               50: dict(target=3000, dd=2000, dll=1250, consist=None, min_dias=1, max_mini=4),
               100: dict(target=6000, dd=3500, dll=2500, consist=None, min_dias=1, max_mini=8),
               150: dict(target=9000, dd=5000, dll=3750, consist=None, min_dias=1, max_mini=12)},
    "select": {25: dict(target=1500, dd=1000, dll=None, consist=0.40, min_dias=3, max_mini=1),
               50: dict(target=3000, dd=2000, dll=None, consist=0.40, min_dias=3, max_mini=4),
               100: dict(target=6000, dd=3000, dll=None, consist=0.40, min_dias=3, max_mini=8),
               150: dict(target=9000, dd=4500, dll=None, consist=0.40, min_dias=3, max_mini=12)},
}
FONDEADA = {
    # Growth: 5 días rentables >= umbral (se reinician por retiro), saldo mínimo, consistencia 35%,
    # retiro mín/máx (1º-3º vs 4º+), DLL suave (pausa del día) que pasa a = DD al alcanzar +6%.
    "growth": {25: dict(dd=1000, dll=600, dia_min=100, saldo_min=1500, cons=0.35, pmin=250, pmax=(1000, 1000), max_mini=1),
               50: dict(dd=2000, dll=1250, dia_min=150, saldo_min=3000, cons=0.35, pmin=500, pmax=(1500, 3000), max_mini=4),
               100: dict(dd=3500, dll=2500, dia_min=200, saldo_min=4500, cons=0.35, pmin=1000, pmax=(2000, 4000), max_mini=8),
               150: dict(dd=5000, dll=3750, dia_min=250, saldo_min=6500, cons=0.35, pmin=1500, pmax=(2500, 5000), max_mini=12)},
    # Select Flex: 5 días ganadores >= umbral, retiro hasta 50% del beneficio, tope oficial; sin DLL ni consistencia.
    "select_flex": {25: dict(dd=1000, dll=None, dia_min=100, frac=0.5, pmax=1250, max_mini=1),
                    50: dict(dd=2000, dll=None, dia_min=150, frac=0.5, pmax=2500, max_mini=4),
                    100: dict(dd=3000, dll=None, dia_min=200, frac=0.5, pmax=3500, max_mini=8),
                    150: dict(dd=4500, dll=None, dia_min=250, frac=0.5, pmax=4500, max_mini=12)},
    # Select Daily: retiro diario de hasta 2x lo ganado desde el último retiro, dejando un colchón; DLL suave.
    "select_daily": {25: dict(dd=1000, dll=500, buffer=1100, pmin=250, pmax=600, max_mini=1),
                     50: dict(dd=2000, dll=1000, buffer=2100, pmin=250, pmax=1250, max_mini=4),
                     100: dict(dd=2500, dll=1250, buffer=2600, pmin=250, pmax=1750, max_mini=8),
                     150: dict(dd=3500, dll=1750, buffer=3600, pmin=250, pmax=2500, max_mini=12)},
    # Lightning: sin examen. 1º retiro al llegar a objetivo de beneficio; consistencia 20/25/30%.
    "lightning": {25: dict(dd=1000, dll=None, goal=(1500, 1000), cons=(0.20, 0.25, 0.30), pmin=1000, pmax=1000, max_mini=1),
                  50: dict(dd=2000, dll=1250, goal=(3000, 2000), cons=(0.20, 0.25, 0.30), pmin=1000, pmax=2000, max_mini=4),
                  100: dict(dd=4000, dll=2500, goal=(6000, 3500), cons=(0.20, 0.25, 0.30), pmin=1000, pmax=2500, max_mini=8),
                  150: dict(dd=5250, dll=3000, goal=(9000, 4500), cons=(0.20, 0.25, 0.30), pmin=1000, pmax=3000, max_mini=12)},
}
SPLIT = 0.90
MAX_CUENTAS_POR_PLAN = 5
REGLAS_DURAS = [
    "Prohibido hedging (posiciones opuestas) y mezclar minis y micros a la vez.",
    "Más del 50% de trades y del 50% del beneficio deben venir de trades de más de 10 segundos.",
    "Cierre obligatorio antes de las 16:59 ET (algunas fuentes: 16:45). Sin posiciones overnight.",
    "HFT/bots de terceros prohibidos; algoritmos propios demostrables permitidos.",
    "Noticias: permitidas.",
]
# Costos por contrato ida y vuelta (comisión all-in + 1 tick de deslizamiento por lado)
COSTO_RT = {"NQ": 5.76 + 2 * 5.0, "MNQ": 1.82 + 2 * 0.5}
USD_PUNTO = {"NQ": 20.0, "MNQ": 2.0}
