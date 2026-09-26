"""Panel de todas las monedas USDT de Binance (spot y perpetuos), velas 1d y 1h."""
import glob, io, os, re, zipfile
import numpy as np
import pandas as pd

DIR = "/home/user/data/cripto/eco"
MEMES = {"DOGE", "SHIB", "PEPE", "FLOKI", "BONK", "WIF", "BOME", "MEME", "TURBO", "NEIRO", "PNUT", "ACT", "MOODENG",
         "PEOPLE", "1000SATS", "ORDI", "DOGS", "HMSTR", "CAT", "POPCAT", "MEW", "BRETT", "GOAT", "CHILLGUY", "PENGU",
         "TRUMP", "FARTCOIN", "BABYDOGE", "BAN", "MUBARAK", "BROCCOLI", "TST", "LUCE", "SLERF", "MYRO", "BANANAS31",
         "MOG", "SPX", "GIGA", "PONKE", "AI16Z", "ZEREBRO", "FWOG", "SUNDOG", "NEIROETH", "HIPPO", "BIGTIME", "LADYS",
         "COQ", "AIDOGE", "ELON", "KISHU", "SAMO", "WOJAK", "BABY", "PUMP", "BOMEUSDT", "1000CHEEMS", "CHEEMS", "WLFI"}


def _zip(f):
    try:
        with zipfile.ZipFile(f) as z:
            raw = z.read(z.namelist()[0])
    except Exception:
        return None
    df = pd.read_csv(io.BytesIO(raw), header=None, usecols=[0, 1, 2, 3, 4, 7])
    if not str(df.iloc[0, 0]).isdigit():
        df = df.iloc[1:]
    df.columns = ["t", "o", "h", "l", "c", "qv"]
    df = df.astype(float)
    t = df["t"].astype("int64")
    t = np.where(t > 1e14, t // 1000, t)        # spot 2025+ usa microsegundos
    df["t"] = pd.to_datetime(t, unit="ms", utc=True)
    return df


def panel(mercado="spot", tf="1d"):
    """Long DataFrame sym,t,o,h,l,c,qv (qv = volumen en USDT)."""
    cache = f"{DIR}/panel_{mercado}_{tf}.parquet"
    if os.path.exists(cache):
        return pd.read_parquet(cache)
    pref = "spot_monthly_klines_" if mercado == "spot" else "futures_um_monthly_klines_"
    fs = sorted(glob.glob(f"{DIR}/k/{pref}*_{tf}_*.zip"))
    partes = []
    for f in fs:
        sym = os.path.basename(f)[len(pref):].split("_")[0]
        d = _zip(f)
        if d is not None and len(d):
            d["sym"] = sym
            partes.append(d)
    df = pd.concat(partes).drop_duplicates(["sym", "t"]).sort_values(["sym", "t"]).reset_index(drop=True)
    df["sym"] = df["sym"].astype("category")
    df.to_parquet(cache)
    return df


def base(sym):
    s = re.sub(r"USDT$", "", sym)
    return re.sub(r"^1000+", "", s) if s.startswith("1000") and s not in ("1000SATS", "1000CHEEMS") else s
