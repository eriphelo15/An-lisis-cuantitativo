"""Fechas de calendario: FOMC (comunicado 14:00 ET; verificado con federalreserve.gov para 2021+), fin de mes, OPEX, festivos."""
import numpy as np, pandas as pd

FOMC = pd.to_datetime("""2010-11-03 2010-12-14 2011-01-26 2011-03-15 2011-04-27 2011-06-22 2011-08-09 2011-09-21 2011-11-02 2011-12-13
2012-01-25 2012-03-13 2012-04-25 2012-06-20 2012-08-01 2012-09-13 2012-10-24 2012-12-12 2013-01-30 2013-03-20 2013-05-01 2013-06-19
2013-07-31 2013-09-18 2013-10-30 2013-12-18 2014-01-29 2014-03-19 2014-04-30 2014-06-18 2014-07-30 2014-09-17 2014-10-29 2014-12-17
2015-01-28 2015-03-18 2015-04-29 2015-06-17 2015-07-29 2015-09-17 2015-10-28 2015-12-16 2016-01-27 2016-03-16 2016-04-27 2016-06-15
2016-07-27 2016-09-21 2016-11-02 2016-12-14 2017-02-01 2017-03-15 2017-05-03 2017-06-14 2017-07-26 2017-09-20 2017-11-01 2017-12-13
2018-01-31 2018-03-21 2018-05-02 2018-06-13 2018-08-01 2018-09-26 2018-11-08 2018-12-19 2019-01-30 2019-03-20 2019-05-01 2019-06-19
2019-07-31 2019-09-18 2019-10-30 2019-12-11 2020-01-29 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16
2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15 2022-01-26 2022-03-16 2022-05-04 2022-06-15
2022-07-27 2022-09-21 2022-11-02 2022-12-14 2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13
2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18 2025-01-29 2025-03-19 2025-05-07 2025-06-18
2025-07-30 2025-09-17 2025-10-29 2025-12-10 2026-01-28""".split())


def marcas(fechas):
    f = pd.DatetimeIndex(fechas)
    C = pd.DataFrame(index=f)
    C["fomc"] = f.isin(FOMC)
    C["pre_fomc"] = pd.Series(f.isin(FOMC), index=f).shift(-1, fill_value=False).to_numpy()
    mes = f.to_period("M")
    s = pd.Series(np.arange(len(f)), index=f)
    C["dia_mes"] = s.groupby(mes).rank().astype(int).to_numpy()            # 1 = primer día hábil
    C["dia_mes_fin"] = s.groupby(mes).rank(ascending=False).astype(int).to_numpy()  # 1 = último día hábil
    C["tom"] = np.where(C.dia_mes_fin <= 2, -C.dia_mes_fin, np.where(C.dia_mes <= 3, C.dia_mes, 0))   # -2,-1,1,2,3
    tercer_viernes = (f.dayofweek == 4) & (f.day >= 15) & (f.day <= 21)
    C["opex"] = tercer_viernes
    C["cuadruple"] = tercer_viernes & f.month.isin([3, 6, 9, 12])
    C["post_opex"] = pd.Series(tercer_viernes, index=f).shift(1, fill_value=False).to_numpy()
    # festivo: el siguiente día hábil en el calendario no aparece en los datos
    sig = pd.Series(f, index=f).shift(-1)
    bd = f + pd.offsets.BDay(1)
    C["pre_festivo"] = (sig.to_numpy() != bd.to_numpy()) & sig.notna().to_numpy()
    C["dow"] = f.dayofweek
    return C
