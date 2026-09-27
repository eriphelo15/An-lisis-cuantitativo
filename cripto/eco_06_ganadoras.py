"""¿Quiénes hicieron ×10 / ×100 en Binance, cuándo, y qué había que aguantar para cobrarlo?"""
import numpy as np
import pandas as pd
import eco_base as e

d = e.panel("spot", "1d"); d["sym"] = d.sym.astype(str)
d = d[~d.sym.str.contains(r"(?:UP|DOWN|BULL|BEAR)USDT$")]
L = pd.read_csv("res_eco_listados.csv", parse_dates=["t0"])
filas = []
for s in L.sym:
    x = d[d.sym == s].set_index("t")
    p0 = x.c.iloc[0]
    imax = x.h.idxmax()
    antes = x.loc[:imax]
    # peor caída desde un máximo previo ANTES de llegar al pico (lo que había que aguantar)
    dd = (antes.l / antes.h.cummax()).min() - 1
    # desde el listado: mínimo antes del pico
    filas.append(dict(sym=s, meme=e.base(s) in e.MEMES, t0=x.index[0], pico=imax, dias_al_pico=(imax - x.index[0]).days,
                      mult_pico=x.h.max() / p0, mult_hoy=x.c.iloc[-1] / p0, caida_en_el_camino=dd,
                      desde_pico_hoy=x.c.iloc[-1] / x.h.max() - 1, activo=x.index[-1] == d.t.max()))
G = pd.DataFrame(filas)
n = len(G)
print(f"Monedas nuevas en Binance desde 2017-09: {n}")
for k in [2, 5, 10, 20, 50, 100]:
    g = G[G.mult_pico >= k]
    print(f"  llegaron a x{k:<3d} en algún momento: {len(g):4d} ({len(g)/n:.1%}) | siguen x{k}+ hoy: {(G.mult_hoy>=k).sum():3d}"
          f" | días medianos hasta el pico: {g.dias_al_pico.median():.0f} | caída mediana que hubo que aguantar antes del pico: {g.caida_en_el_camino.median():.0%}")
print("\nTodas las que hicieron x10 o más desde su listado en Binance:")
w = G[G.mult_pico >= 10].sort_values("mult_pico", ascending=False)
for r in w.itertuples():
    print(f"  {r.sym:14s} {'MEME' if r.meme else '    '} listada {r.t0:%Y-%m} pico x{r.mult_pico:6.1f} en {r.dias_al_pico:4d} días"
          f" | caída aguantada antes {r.caida_en_el_camino:+.0%} | hoy x{r.mult_hoy:5.2f} ({r.desde_pico_hoy:+.0%} desde el pico)")
print("\nPor año de listado: % que llegó a x10")
print(G.groupby(G.t0.dt.year).apply(lambda g: f"n={len(g):3d}  x10: {(g.mult_pico>=10).mean():.1%}  x5: {(g.mult_pico>=5).mean():.1%}").to_string())
G.to_csv("res_eco_ganadoras.csv", index=False)
