"""Dibuja cómo está programado el VI original del usuario sobre operaciones reales de NQ (enero 2026)."""
import sys, importlib
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "../estudio_nq")
vi = importlib.import_module("22_vi_usuario")
A, E20, E50, F, atr = vi.dias_con_ema("NQ"); tick = 0.25

def operar(di, n, d):
    o, h, l, c = A[di, n]; o1, c1 = A[di, n - 1, 0], A[di, n - 1, 3]
    tp = max(o, c) if d > 0 else min(o, c)     # borde del hueco (TP)
    tp = min(o1, c1) if d > 0 else max(o1, c1)  # hueco completo: cuerpo de la vela anterior
    tp_borde = max(o, c) if d > 0 else min(o, c)
    for k in range(n + 1, min(n + 5, 389) + 1):
        hh, ll, cc = A[di, k, 1], A[di, k, 2], A[di, k, 3]
        if (d > 0 and hh >= tp_borde + tick) or (d < 0 and ll <= tp_borde - tick): return k, tp_borde, "TP (hueco)", d * (tp_borde - c)
        if (d > 0 and cc < E20[di, k]) or (d < 0 and cc > E20[di, k]): return k, cc, "cierre al otro lado de EMA20", d * (cc - c)
        if k == n + 5: return k, cc, "5 minutos", d * (cc - c)

def dibujar(ax, fecha, hora, titulo):
    di = int(np.flatnonzero(F == pd.Timestamp(fecha))[0])
    n = (pd.Timestamp(f"2000-01-01 {hora}") - pd.Timestamp("2000-01-01 09:30")).seconds // 60
    o, h, l, c = A[di, n]; d = -1 if E20[di, n] < E50[di, n] else 1
    k, px, mot, res = operar(di, n, d)
    a, b = n - 12, k + 6; x = np.arange(a, b)
    for t in x:
        oo, hh, ll, cc = A[di, t]; col = "#1f1f1f" if cc < oo else "#ffffff"
        ax.vlines(t, ll, hh, color="#1f1f1f", lw=1)
        ax.add_patch(plt.Rectangle((t - 0.35, min(oo, cc)), 0.7, max(abs(cc - oo), 0.25), facecolor=col, edgecolor="#1f1f1f", lw=1))
    ax.plot(x, E20[di, a:b], color="#3b9ae1", lw=2, label="EMA 20"); ax.plot(x, E50[di, a:b], color="#f0a030", lw=2, label="EMA 50")
    # hueco VI
    o1, c1 = A[di, n - 1, 0], A[di, n - 1, 3]
    g_lo, g_hi = (max(o1, c1), min(o, c)) if d < 0 else (max(o, c), min(o1, c1))
    ax.add_patch(plt.Rectangle((n - 1.45, g_lo - 0.6), 1.9, (g_hi - g_lo) + 1.2, facecolor="#c77dff", alpha=0.55, edgecolor="#7b2cbf", lw=1.5, zorder=4))
    ax.annotate("VI: hueco entre cuerpos\n(vela contra la tendencia)", (n - 0.4, (g_lo + g_hi) / 2), xytext=(n - 11.5, (g_lo + g_hi) / 2 + (8 if d < 0 else -8)),
                arrowprops=dict(arrowstyle="->", color="#555"), fontsize=9, color="#333")
    tp_borde = min(o, c) if d < 0 else max(o, c)
    ax.hlines(c, n, k, color="#555", lw=1.5, ls="--"); ax.hlines(tp_borde, n, k, color="#2e9e4f", lw=1.5, ls="--")
    ax.plot(n, c, marker="v" if d < 0 else "^", ms=12, color="#b03030" if d < 0 else "#2e9e4f", zorder=5)
    ax.text(n + 0.4, c, f" ENTRADA {'VENTA' if d < 0 else 'COMPRA'}\n al cierre de la vela VI", fontsize=9, va="center", color="#333")
    ax.text(n - 0.5, tp_borde - (3 if d < 0 else -3), "TP = borde del hueco", fontsize=9, ha="right", va="top" if d < 0 else "bottom", color="#2e9e4f")
    ax.plot(k, px, marker="X", ms=12, color="#2e9e4f" if res > 0 else "#b03030", zorder=5)
    ax.text(k + 0.6, px + (6 if res > 0 else 0), f" SALIDA: {mot}\n {res:+.2f} pts (${res*20-5.76-(5 if res>0 else 10):+.0f} con 1 NQ)", fontsize=9, va="center",
            color="#2e9e4f" if res > 0 else "#b03030", fontweight="bold")
    ax.set_xticks(x[::3]); ax.set_xticklabels([(pd.Timestamp("2000-01-01 09:30") + pd.Timedelta(minutes=int(t))).strftime("%H:%M") for t in x[::3]], fontsize=8)
    ax.set_title(titulo, fontsize=11, loc="left"); ax.grid(alpha=0.15); ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)

fig, axs = plt.subplots(1, 2, figsize=(16, 6.5))
dibujar(axs[0], "2026-01-13", "10:05", "13-ene-2026 · NQ 1 min · tendencia bajista: VI alcista en contra → VENTA\nEl hueco se llena en 1 minuto: la operación típica (70% de las veces)")
dibujar(axs[1], "2026-01-09", "10:10", "09-ene-2026 · NQ 1 min · tendencia bajista: VI alcista en contra → VENTA\nEl hueco NO se llena y el precio cierra sobre la EMA20: la pérdida típica")
fig.suptitle("Cómo está programado tu VI original: tendencia por EMA20/50 · VI en contra · entrada al cierre · TP en el hueco · salida a 5 min o si cierra al otro lado de la EMA20 · sin stop",
             fontsize=11, y=0.995)
fig.tight_layout(); fig.savefig("vi_original_ejemplos.png", dpi=130)
print("ok")
