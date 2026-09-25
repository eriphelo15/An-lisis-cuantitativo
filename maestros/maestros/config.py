import os
from dataclasses import dataclass
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent


def _cargar_env(ruta: Path) -> None:
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def _variable(nombre: str) -> str | None:
    return os.environ.get(nombre) or None


@dataclass(frozen=True)
class Config:
    sec_user_agent: str | None
    alpaca_key_id: str | None
    alpaca_secret: str | None
    massive_api_key: str | None
    massive_base_url: str
    directorio_datos: Path

    def exigir_sec(self) -> str:
        if not self.sec_user_agent:
            raise RuntimeError('Falta MAESTROS_SEC_USER_AGENT en .env (ejemplo: "Maestros tu-email@ejemplo.com").')
        return self.sec_user_agent

    def exigir_alpaca(self) -> tuple[str, str]:
        if not (self.alpaca_key_id and self.alpaca_secret):
            raise RuntimeError("Faltan ALPACA_API_KEY_ID y ALPACA_API_SECRET_KEY en .env (cuenta gratuita de alpaca.markets).")
        return self.alpaca_key_id, self.alpaca_secret

    def exigir_massive(self) -> str:
        if not self.massive_api_key:
            raise RuntimeError("Falta MASSIVE_API_KEY en .env (plan gratuito de massive.com).")
        return self.massive_api_key


def cargar_config() -> Config:
    _cargar_env(RAIZ_PROYECTO / ".env")
    return Config(
        sec_user_agent=_variable("MAESTROS_SEC_USER_AGENT"),
        alpaca_key_id=_variable("ALPACA_API_KEY_ID"),
        alpaca_secret=_variable("ALPACA_API_SECRET_KEY"),
        massive_api_key=_variable("MASSIVE_API_KEY"),
        massive_base_url=os.environ.get("MASSIVE_BASE_URL", "https://api.polygon.io").rstrip("/"),
        directorio_datos=Path(os.environ.get("MAESTROS_DATOS", RAIZ_PROYECTO / "datos")),
    )
