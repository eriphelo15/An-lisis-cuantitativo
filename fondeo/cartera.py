"""Simulación de cartera: presupuesto de cuotas, hasta 5 cuentas simultáneas, recompra al fallar.
Dos casos extremos de correlación entre cuentas:
  * independientes: cada cuenta opera su propia secuencia (misma política, trades no simultáneos);
  * copiadas: las 5 cuentas replican los mismos trades (resultado idéntico en cada lote).
Entrada: vector de aprobados del examen y vector de cobros de la fondeada (Monte Carlo del motor)."""
import numpy as np

def cartera(p_pass, cobros, precio, presupuesto=1000.0, max_cuentas=5, n=20000, copiadas=False, seed=3):
    rng = np.random.default_rng(seed)
    neto = np.zeros(n); compradas = np.zeros(n); fondeadas = np.zeros(n)
    for i in range(n):
        gastado = 0.0; cobrado = 0.0; nf = 0; nb = 0
        if copiadas:
            while gastado + precio * max_cuentas <= presupuesto + 1e-9:
                gastado += precio * max_cuentas; nb += max_cuentas
                if rng.random() < p_pass:
                    cobrado += max_cuentas * cobros[rng.integers(len(cobros))]; nf += max_cuentas
                    break  # 5 fondeadas ocupan el máximo del plan
        else:
            activos = 0
            while gastado + precio <= presupuesto + 1e-9 and nf < max_cuentas:
                gastado += precio; nb += 1
                if rng.random() < p_pass:
                    cobrado += cobros[rng.integers(len(cobros))]; nf += 1
        neto[i] = cobrado - gastado; compradas[i] = nb; fondeadas[i] = nf
    return dict(ev=neto.mean(), p_ganar=(neto > 0).mean(), p10=np.quantile(neto, .1), p50=np.median(neto),
                p90=np.quantile(neto, .9), peor=neto.min(), examenes=compradas.mean(), fondeadas=fondeadas.mean(), neto=neto)
