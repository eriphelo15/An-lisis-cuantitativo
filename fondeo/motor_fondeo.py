"""Motor Monte Carlo del ciclo de fondeo Tradeify (examen -> fondeada -> retiros).

Hipótesis de mercado: SIN ventaja. Cada trade entra en una dirección aleatoria sobre un día real de NQ
(escalado al precio actual), con stop y objetivo tipo bracket. Así el resultado mide solo el efecto de las
REGLAS de la firma y de la POLÍTICA de apuesta (tamaño, stop/objetivo, trades por día, paradas diarias).

Supuestos conservadores:
  * Entrada al open de la barra de 1 min; si stop y objetivo caen en la misma barra -> stop.
  * Si una barra abre más allá del stop, se llena al open (deslizamiento real por gap).
  * Costos: comisión all-in + 1 tick por lado, por contrato.
  * Drawdown EOD trailing aplicado en tiempo real contra el peor precio de cada barra.
"""
import numpy as np
from numba import njit, prange

TICK = 0.25


@njit(cache=True)
def tamano(riesgo, S, max_micro):
    """Contratos para arriesgar 'riesgo' USD con stop de S pts. Usa minis si caben (más baratos por
    exposición), si no micros; nunca mezcla ambos (regla de la firma). Devuelve (c, usd_pt, costo_rt)."""
    n_mic = int(riesgo / (S * 2.0 + 2.82))
    if n_mic > max_micro:
        n_mic = max_micro
    n_min = int(riesgo / (S * 20.0 + 15.76))
    if n_min > max_micro // 10:
        n_min = max_micro // 10
    if n_min >= 1 and n_min * 10 >= n_mic - 1:
        return float(n_min), 20.0, 15.76
    if n_mic >= 1:
        return float(n_mic), 2.0, 2.82
    return 0.0, 2.0, 2.82


@njit(cache=True)
def sim_dia(D, di, R, S, T, K, G, L, dist_piso, falta_obj, max_micro):
    """Simula un día con tamaño dinámico. R: riesgo USD por trade; S/T: stop/objetivo en pts.
    Devuelve (pnl_día, quiebre, n_trades)."""
    pnl = 0.0
    j = 1
    n = 0
    while n < K and j < 380:
        if pnl >= G or pnl <= -L:
            break
        disp = min(L + pnl, dist_piso + pnl - 1.0)
        riesgo = min(R, disp)
        c, usd, cost = tamano(riesgo, S, max_micro)
        if c <= 0:
            break
        t_eff = T
        if falta_obj > 0:
            need = (falta_obj - pnl + cost * c) / (c * usd)
            need = np.ceil(need / TICK) * TICK
            if need < t_eff:
                t_eff = max(need, TICK)
        d = 1.0 if np.random.random() < 0.5 else -1.0
        e = D[di, j, 0]
        stop = e - d * S
        tgt = e + d * t_eff
        k = j
        salida = D[di, 385, 3]
        kk = 385
        while k <= 385:
            o = D[di, k, 0]; h = D[di, k, 1]; lo = D[di, k, 2]
            if d > 0:
                hs = lo <= stop; ht = h >= tgt
            else:
                hs = h >= stop; ht = lo <= tgt
            if hs:
                px = stop
                if k > j and ((d > 0 and o < stop) or (d < 0 and o > stop)):
                    px = o
                salida = px; kk = k
                break
            if ht:
                salida = tgt; kk = k
                break
            k += 1
        pnl += d * (salida - e) * c * usd - cost * c
        n += 1
        if pnl <= -dist_piso:
            return pnl, True, n
        j = kk + 1
    return pnl, False, n


@njit(cache=True)
def actualizar_piso(max_eod, dd):
    # piso relativo al saldo inicial (0). Se congela en +100 al superar dd+100.
    if max_eod >= dd + 100.0:
        return 100.0
    return max_eod - dd


@njit(parallel=True, cache=True)
def examen(D, nsim, target, dd, dll, consist, min_dias, R, S, T, K, G, L, max_micro, max_dias, seed):
    """Devuelve (aprobado[nsim], dias[nsim])."""
    ok = np.zeros(nsim, np.bool_)
    dias = np.zeros(nsim, np.int32)
    nd = D.shape[0]
    for i in prange(nsim):
        np.random.seed(seed + i)
        p = 0.0; max_eod = 0.0; piso = -dd; best = 0.0
        for dia in range(max_dias):
            Ld = L if dll <= 0 else min(L, dll)
            Gd = G
            if consist > 0:
                # no dejar que un día supere la consistencia sobre el objetivo
                Gd = min(G, consist * target * 0.95)
            falta = target - p if (consist <= 0 or best <= consist * target) else 0.0
            di = np.random.randint(nd)
            r, q, n = sim_dia(D, di, R, S, T, K, Gd, Ld, p - piso, falta, max_micro)
            p += r
            dias[i] = dia + 1
            if q or p <= piso or p - piso < S * 2.0 + 3.0:
                break
            if r > best:
                best = r
            if p > max_eod:
                max_eod = p
            piso = actualizar_piso(max_eod, dd)
            if p >= target and dia + 1 >= min_dias and (consist <= 0 or best <= consist * p):
                ok[i] = True
                break
    return ok, dias


@njit(parallel=True, cache=True)
def fondeada(D, nsim, tipo, size_k, dd, dll, dia_min, saldo_min, cons, pmin, pmax1, pmax4, frac, buffer_,
             goal1, goal2, R, S, T, K, G, L, max_micro, reserva, horizonte, seed):
    """tipo: 0 growth, 1 select_flex, 2 select_daily, 3 lightning.
    Devuelve (cobrado_neto[nsim], n_retiros[nsim], dias_vivos[nsim], quebrada[nsim])."""
    cobrado = np.zeros(nsim); nret = np.zeros(nsim, np.int32); vivos = np.zeros(nsim, np.int32)
    quebro = np.zeros(nsim, np.bool_)
    nd = D.shape[0]
    seis = 0.06 * size_k * 1000.0
    for i in prange(nsim):
        np.random.seed(seed + i)
        p = 0.0; max_eod = 0.0; piso = -dd
        buenos = 0; ciclo = 0.0; mejor = 0.0; k = 0
        for dia in range(horizonte):
            Ld = L
            if dll > 0 and p < seis:
                Ld = min(L, dll)
            Gd = G
            if tipo == 0 and cons > 0:
                Gd = G  # la política ya fija G bajo la consistencia
            di = np.random.randint(nd)
            r, q, n = sim_dia(D, di, R, S, T, K, Gd, Ld, p - piso, 0.0, max_micro)
            p += r
            vivos[i] = dia + 1
            if q or p <= piso or p - piso < S * 2.0 + 3.0:
                quebro[i] = True
                break
            ciclo += r
            if r > mejor:
                mejor = r
            if r >= dia_min:
                buenos += 1
            if p > max_eod:
                max_eod = p
            piso = actualizar_piso(max_eod, dd)
            monto = 0.0
            if tipo == 0:  # Growth
                if buenos >= 5 and p >= saldo_min and ciclo > 0 and mejor <= cons * ciclo:
                    tope = pmax1 if k < 3 else pmax4
                    monto = min(tope, p - 100.0 - reserva)
                    if monto < pmin:
                        monto = 0.0
            elif tipo == 1:  # Select Flex
                if buenos >= 5 and p > 0:
                    monto = min(pmax1, frac * p)
                    if monto < 250.0:
                        monto = 0.0
            elif tipo == 2:  # Select Daily
                if p - buffer_ >= pmin and ciclo > 0:
                    monto = min(pmax1, 2.0 * ciclo, p - buffer_)
                    if monto < pmin:
                        monto = 0.0
            else:  # Lightning
                meta = goal1 if k == 0 else goal2
                cc = 0.20 if k == 0 else (0.25 if k == 1 else 0.30)
                if ciclo >= meta and mejor <= cc * ciclo:
                    monto = min(pmax1, p - 100.0 - reserva)
                    if monto < pmin:
                        monto = 0.0
            if monto > 0:
                p -= monto
                cobrado[i] += 0.9 * monto
                nret[i] += 1
                k += 1
                buenos = 0; ciclo = 0.0; mejor = 0.0
    return cobrado, nret, vivos, quebro
