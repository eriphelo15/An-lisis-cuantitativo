import json
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from maestros.datos.alpaca import COLUMNAS_BARRAS
from maestros.datos.calendario import dias_habiles
from maestros.datos.massive import COLUMNAS_DIARIO
from maestros.informacion.catalizadores import Noticia


class Almacen:
    """Datos locales en Parquet (barras) y JSON Lines (noticias), organizados por fecha."""

    def __init__(self, raiz: Path):
        self.raiz = raiz

    def _diario(self, fecha: date) -> Path:
        return self.raiz / "diario" / f"{fecha.isoformat()}.parquet"

    def _minutos(self, fecha: date, ticker: str) -> Path:
        return self.raiz / "minutos" / fecha.isoformat() / f"{ticker}.parquet"

    def _noticias(self, fecha: date) -> Path:
        return self.raiz / "noticias" / f"{fecha.isoformat()}.jsonl"

    @staticmethod
    def _escribir(ruta: Path, df: pd.DataFrame) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(ruta, index=False)

    def tiene_diario(self, fecha: date) -> bool:
        return self._diario(fecha).exists()

    def guardar_diario(self, fecha: date, df: pd.DataFrame) -> None:
        self._escribir(self._diario(fecha), df)

    def cargar_diario(self, desde: date, hasta: date) -> pd.DataFrame:
        partes = [pd.read_parquet(self._diario(d)) for d in dias_habiles(desde, hasta) if self.tiene_diario(d)]
        partes = [p for p in partes if not p.empty]
        if not partes:
            return pd.DataFrame(columns=COLUMNAS_DIARIO)
        df = pd.concat(partes, ignore_index=True)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
        return df

    def tiene_minutos(self, fecha: date, ticker: str) -> bool:
        return self._minutos(fecha, ticker).exists()

    def guardar_minutos(self, fecha: date, ticker: str, df: pd.DataFrame) -> None:
        self._escribir(self._minutos(fecha, ticker), df)

    def cargar_minutos(self, fecha: date, ticker: str) -> pd.DataFrame:
        ruta = self._minutos(fecha, ticker)
        return pd.read_parquet(ruta) if ruta.exists() else pd.DataFrame(columns=COLUMNAS_BARRAS)

    def tiene_noticias(self, fecha: date) -> bool:
        return self._noticias(fecha).exists()

    def guardar_noticias(self, fecha: date, noticias: list[Noticia]) -> None:
        ruta = self._noticias(fecha)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        lineas = [json.dumps({**asdict(n), "hora": n.hora.isoformat()}) for n in noticias]
        ruta.write_text("\n".join(lineas), encoding="utf-8")

    def cargar_noticias(self, fecha: date) -> list[Noticia]:
        ruta = self._noticias(fecha)
        if not ruta.exists():
            return []
        noticias = []
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                d = json.loads(linea)
                noticias.append(Noticia(**{**d, "tickers": tuple(d["tickers"]), "hora": datetime.fromisoformat(d["hora"])}))
        return noticias

    def carpeta_resultados(self, nombre: str) -> Path:
        ruta = self.raiz / "resultados" / nombre
        ruta.mkdir(parents=True, exist_ok=True)
        return ruta
