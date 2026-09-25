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


@dataclass(frozen=True)
class Config:
    sec_user_agent: str | None
    massive_api_key: str | None
    massive_base_url: str
    directorio_datos: Path

    def exigir_sec(self) -> str:
        if not self.sec_user_agent:
            raise RuntimeError(
                "Falta HERMES_SEC_USER_AGENT en .env. La SEC exige nombre y email, "
                "por ejemplo: HERMES_SEC_USER_AGENT=\"Hermes tu-email@ejemplo.com\""
            )
        return self.sec_user_agent

    def exigir_massive(self) -> str:
        if not self.massive_api_key:
            raise RuntimeError("Falta MASSIVE_API_KEY en .env (la cuenta gratuita de massive.com sirve).")
        return self.massive_api_key


def cargar_config() -> Config:
    _cargar_env(RAIZ_PROYECTO / ".env")
    return Config(
        sec_user_agent=os.environ.get("HERMES_SEC_USER_AGENT") or None,
        massive_api_key=os.environ.get("MASSIVE_API_KEY") or None,
        massive_base_url=os.environ.get("MASSIVE_BASE_URL", "https://api.polygon.io").rstrip("/"),
        directorio_datos=Path(os.environ.get("HERMES_DATOS", RAIZ_PROYECTO / "datos")),
    )
