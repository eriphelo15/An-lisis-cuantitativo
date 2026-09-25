import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Any

import requests

REINTENTOS = 4
ESTADOS_REINTENTABLES = {429, 500, 502, 503, 504}


class NoEncontrado(Exception):
    pass


class LimitadorTasa:
    def __init__(self, llamadas_por_segundo: float):
        self._intervalo = 1.0 / llamadas_por_segundo
        self._ultimo = 0.0
        self._lock = threading.Lock()

    def esperar(self) -> None:
        with self._lock:
            espera = self._ultimo + self._intervalo - time.monotonic()
            if espera > 0:
                time.sleep(espera)
            self._ultimo = time.monotonic()


class ClienteHTTP:
    """Límite de tasa, reintentos y caché en disco.

    `ttl_segundos=None` guarda la respuesta para siempre (solo para datos que ya no cambian);
    `ttl_segundos=0` no usa caché. Los headers no forman parte de la clave de caché: ahí van las claves secretas.
    """

    def __init__(
        self,
        user_agent: str,
        llamadas_por_segundo: float,
        dir_cache: Path | None = None,
        headers_extra: dict[str, str] | None = None,
        sesion: requests.Session | None = None,
        timeout: float = 30.0,
    ):
        self._headers = {"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate", **(headers_extra or {})}
        self._limitador = LimitadorTasa(llamadas_por_segundo)
        self._dir_cache = dir_cache
        self._sesion = sesion or requests.Session()
        self._timeout = timeout
        if dir_cache:
            dir_cache.mkdir(parents=True, exist_ok=True)

    def _ruta_cache(self, metodo: str, url: str, params: dict | None, cuerpo: Any) -> Path | None:
        if not self._dir_cache:
            return None
        clave = json.dumps([metodo, url, params or {}, cuerpo], sort_keys=True, default=str)
        return self._dir_cache / f"{hashlib.sha256(clave.encode()).hexdigest()}.cache"

    def pedir(
        self,
        url: str,
        params: dict | None = None,
        ttl_segundos: float | None = 0,
        metodo: str = "GET",
        cuerpo_json: Any = None,
    ) -> bytes:
        ruta = self._ruta_cache(metodo, url, params, cuerpo_json)
        if ruta and ruta.exists() and ttl_segundos != 0:
            if ttl_segundos is None or time.time() - ruta.stat().st_mtime < ttl_segundos:
                return ruta.read_bytes()

        for intento in range(REINTENTOS):
            self._limitador.esperar()
            resp = self._sesion.request(
                metodo, url, params=params, json=cuerpo_json, headers=self._headers, timeout=self._timeout
            )
            if resp.status_code == 404:
                raise NoEncontrado(url)
            if resp.status_code in ESTADOS_REINTENTABLES and intento < REINTENTOS - 1:
                time.sleep(2 ** (intento + 1))
                continue
            resp.raise_for_status()
            break

        if ruta and ttl_segundos != 0:
            ruta.write_bytes(resp.content)
        return resp.content

    def pedir_json(self, url: str, **kwargs) -> Any:
        return json.loads(self.pedir(url, **kwargs))

    def pedir_texto(self, url: str, **kwargs) -> str:
        return self.pedir(url, **kwargs).decode("utf-8", errors="replace")
