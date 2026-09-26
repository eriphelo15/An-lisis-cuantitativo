"""Oro: deriva por tramo horario, predictibilidad tramo->tramo, y días de Fed/IPC/empleo. En bp, por mitad de periodo."""
import sys, itertools
import numpy as np, pandas as pd
from base_oro import cargar, idx, PER
sys.path.insert(0, "../brechas")
from calendario import FOMC
NFP = pd.to_datetime(open("/home/user/data/ext/release_PAYEMS.txt").read().split()); CPI = pd.to_datetime(open("/home/user/data/ext/release_CPIAUCSL.txt").read().split())
A, E20, E50, F, ref = cargar()
CUT = {"18:00": 1800, "20:00": 2000, "00:00": 0, "03:00 Londres": 300, "05:00": 500, "08:20 COMEX": 820, "09:30": 930, "10:30": 1030, "12:00": 1200,
       "13:30 cierre COMEX": 1330, "16:00": 1600, "16:59": 1659}
px = {k: A[:, idx(v), 0] for k, v in CUT.items()}
P = np.array([next((t for t, a, b in PER if a <= str(f.date()) <= b), "") for f in F])
st = lambda x: f"{np.nanmean(x):+6.1f}bp t={np.nanmean(x)/np.nanstd(x)*np.sqrt(np.sum(~np.isnan(x))):+4.1f}"
ks = list(CUT)
print("== Deriva media por tramo (bp)")
for a, b in zip(ks[:-1], ks[1:]):
    r = (px[b] - px[a]) / ref * 1e4
    print(f"  {a:>18s} -> {b:18s}", " | ".join(f"{t[:3]}: {st(r[P == t])}" for t, _, _ in PER))
r_d = (px["16:59"] - px["18:00"]) / ref * 1e4
print(f"  {'día completo':>40s}", " | ".join(f"{t[:3]}: {st(r_d[P == t])}" for t, _, _ in PER))
print("\n== Predictibilidad: signo(tramo previo) x tramo siguiente (bp) — solo pares con |t|>=2 en ambas mitades y mismo signo")
for i, j, k2 in itertools.combinations(range(len(ks)), 3):
    a, b, c = ks[i], ks[j], ks[k2]
    x = np.sign(px[b] - px[a]) * (px[c] - px[b]) / ref * 1e4
    ts_ = [np.nanmean(x[P == t]) / np.nanstd(x[P == t]) * np.sqrt(np.sum(P == t)) for t, _, _ in PER]
    if all(abs(v) >= 2 for v in ts_) and np.sign(ts_[0]) == np.sign(ts_[1]):
        print(f"  {a}->{b} predice {b}->{c}:", " | ".join(f"{t[:3]}: {st(x[P == t])}" for t, _, _ in PER))
print("\n== Días de evento (bp)")
for nom, fechas in [("FOMC", FOMC), ("IPC", CPI), ("Empleo", NFP)]:
    m = F.isin(fechas)
    for tn, (a, b) in {"víspera 18:00->08:20": ("18:00", "08:20 COMEX"), "08:20->13:30": ("08:20 COMEX", "13:30 cierre COMEX"), "día completo": ("18:00", "16:59")}.items():
        r = (px[b] - px[a]) / ref * 1e4
        print(f"  {nom:6s} {tn:22s}", " | ".join(f"{t[:3]}: {st(r[m & (P == t)])} n={np.sum(m & (P == t))}" for t, _, _ in PER))
