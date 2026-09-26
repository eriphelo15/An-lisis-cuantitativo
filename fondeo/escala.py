"""Simulación de escala en el tiempo: caja inicial, reinversión de retiros, 5 cupos fondeados por plan
(Growth 50K y Select 50K -> Flex), exámenes para rellenar cupos vacíos. Día a día durante H días hábiles.

Correlación: con 'dia_comun' todas las cuentas operan el MISMO día de mercado (realista si usan la misma
regla y hora); sin él, cada cuenta recibe un día independiente (cota superior: cuentas diversificadas por
instrumento/horario). La realidad queda entre ambos.
"""
import numpy as np
from numba import njit
from motor_fondeo import sim_dia, actualizar_piso

# índices de parámetros por plan (vector float64)
# 0 cuota, 1 target, 2 dd, 3 dll_examen, 4 consist, 5 min_dias,
# 6 eR, 7 eS, 8 eT, 9 eK, 10 eG,
# 11 tipo_fondeada (0 growth, 1 flex), 12 dll_f, 13 dia_min, 14 saldo_min, 15 cons_f, 16 pmin, 17 pmax1, 18 pmax4, 19 frac,
# 20 fR, 21 fS, 22 fT, 23 fK, 24 fG, 25 colchon, 26 activo


@njit(cache=True)
def escala(D, npaths, H, caja0, P, modo, t_ini, dia_comun, max_f, seed, max_ex=5, TV=None, aporte=0.0):
    nplan = P.shape[0]
    caja_fin = np.zeros(npaths); gastado = np.zeros(npaths); cobrado = np.zeros(npaths)
    n_exam = np.zeros(npaths); n_fond = np.zeros(npaths)
    curva = np.zeros((npaths, H))
    nd = D.shape[0]
    ME = 5  # capacidad del arreglo; el límite efectivo es max_ex
    for ip in range(npaths):
        np.random.seed(seed + ip)
        caja = caja0
        # exámenes: estado [activo, p, max_eod, piso, best, dias]
        ex = np.zeros((nplan, ME, 6))
        # fondeadas: [activa, p, max_eod, piso, buenos, ciclo, mejor, k]
        fo = np.zeros((nplan, max_f, 8))
        for t in range(H):
            if t > 0 and t % 21 == 0:
                caja += aporte
            # comprar exámenes para rellenar cupos vacíos
            for pl in range(nplan):
                if P[pl, 26] < 0.5:
                    continue
                nf = 0
                for a in range(max_f):
                    if fo[pl, a, 0] > 0.5:
                        nf += 1
                ne = 0
                for a in range(ME):
                    if ex[pl, a, 0] > 0.5:
                        ne += 1
                for a in range(ME):
                    if nf + ne >= max_f or ne >= max_ex:
                        break
                    if ex[pl, a, 0] < 0.5 and caja >= P[pl, 0]:
                        caja -= P[pl, 0]; gastado[ip] += P[pl, 0]; n_exam[ip] += 1
                        ex[pl, a, 0] = 1.0; ex[pl, a, 1] = 0.0; ex[pl, a, 2] = 0.0
                        ex[pl, a, 3] = -P[pl, 2]; ex[pl, a, 4] = 0.0; ex[pl, a, 5] = 0.0
                        ne += 1
            dcom = np.random.randint(nd)
            for pl in range(nplan):
                if P[pl, 26] < 0.5:
                    continue
                tgt = P[pl, 1]; dd = P[pl, 2]; cons = P[pl, 4]
                # ---- exámenes
                for a in range(ME):
                    if ex[pl, a, 0] < 0.5:
                        continue
                    p = ex[pl, a, 1]; piso = ex[pl, a, 3]; best = ex[pl, a, 4]
                    Ld = 1e9 if P[pl, 3] <= 0 else P[pl, 3]
                    Gd = P[pl, 10]
                    falta = tgt - p if (cons <= 0 or best <= cons * tgt) else 0.0
                    di = dcom if dia_comun else np.random.randint(nd)
                    r, q, n = sim_dia(D, di, P[pl, 6], P[pl, 7], P[pl, 8], int(P[pl, 9]), Gd, Ld, p - piso, falta, 40, modo, int(TV[pl, a]) if TV is not None else t_ini)
                    p += r; ex[pl, a, 5] += 1
                    if q or p <= piso or p - piso < P[pl, 7] * 2 + 3 or ex[pl, a, 5] >= 60:
                        ex[pl, a, 0] = 0.0
                        continue
                    if r > best:
                        best = r
                    if p > ex[pl, a, 2]:
                        ex[pl, a, 2] = p
                    piso = actualizar_piso(ex[pl, a, 2], dd)
                    ex[pl, a, 1] = p; ex[pl, a, 3] = piso; ex[pl, a, 4] = best
                    if p >= tgt and ex[pl, a, 5] >= P[pl, 5] and (cons <= 0 or best <= cons * p):
                        ex[pl, a, 0] = 0.0
                        for b in range(max_f):
                            if fo[pl, b, 0] < 0.5:
                                fo[pl, b, :] = 0.0
                                fo[pl, b, 0] = 1.0; fo[pl, b, 3] = -dd
                                n_fond[ip] += 1
                                break
                # ---- fondeadas
                for b in range(max_f):
                    if fo[pl, b, 0] < 0.5:
                        continue
                    p = fo[pl, b, 1]; piso = fo[pl, b, 3]
                    Ld = 1e9
                    if P[pl, 12] > 0 and p < 3000.0:
                        Ld = P[pl, 12]
                    di = dcom if dia_comun else np.random.randint(nd)
                    r, q, n = sim_dia(D, di, P[pl, 20], P[pl, 21], P[pl, 22], int(P[pl, 23]), P[pl, 24], Ld, p - piso, 0.0, 40, modo, int(TV[pl, b]) if TV is not None else t_ini)
                    p += r
                    if q or p <= piso or p - piso < P[pl, 21] * 2 + 3:
                        fo[pl, b, 0] = 0.0
                        continue
                    fo[pl, b, 5] += r
                    if r > fo[pl, b, 6]:
                        fo[pl, b, 6] = r
                    if r >= P[pl, 13]:
                        fo[pl, b, 4] += 1
                    if p > fo[pl, b, 2]:
                        fo[pl, b, 2] = p
                    piso = actualizar_piso(fo[pl, b, 2], dd)
                    monto = 0.0
                    if P[pl, 11] < 0.5:  # growth
                        if fo[pl, b, 4] >= 5 and p >= P[pl, 14] and fo[pl, b, 5] > 0 and fo[pl, b, 6] <= P[pl, 15] * fo[pl, b, 5]:
                            tope = P[pl, 17] if fo[pl, b, 7] < 3 else P[pl, 18]
                            if P[pl, 25] >= 0:
                                monto = tope if p - tope >= P[pl, 25] else 0.0
                            else:
                                monto = min(tope, p - 100.0)
                            if monto < P[pl, 16]:
                                monto = 0.0
                    else:  # select flex
                        if fo[pl, b, 4] >= 5 and p > 0:
                            monto = min(P[pl, 17], P[pl, 19] * p)
                            if monto < 250.0:
                                monto = 0.0
                    if monto > 0:
                        p -= monto; caja += 0.9 * monto; cobrado[ip] += 0.9 * monto
                        fo[pl, b, 7] += 1; fo[pl, b, 4] = 0; fo[pl, b, 5] = 0.0; fo[pl, b, 6] = 0.0
                    fo[pl, b, 1] = p; fo[pl, b, 3] = piso
            curva[ip, t] = caja
        caja_fin[ip] = caja
    return caja_fin, gastado, cobrado, n_exam, n_fond, curva


def params(plan):
    """Parámetros de la política elegida (entrada momentum de apertura) para cada plan 50K."""
    v = np.zeros(27)
    if plan == "growth":
        v[:11] = [93., 3000., 2000., 1250., 0., 1., 2000., 60., 180., 2., 1e9]
        v[11:20] = [0., 1250., 150., 3000., 0.35, 500., 1500., 3000., 0.]
        v[20:27] = [250., 60., 120., 2., 600., 2500., 1.]
    else:
        v[:11] = [99., 3000., 2000., 0., 0.40, 3., 300., 60., 240., 1., 960.]
        v[11:20] = [1., 0., 150., 0., 0., 250., 2500., 2500., 0.5]
        v[20:27] = [150., 60., 120., 1., 1e9, -1., 1.]
    return v
