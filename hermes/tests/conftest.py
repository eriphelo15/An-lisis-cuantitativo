from datetime import datetime

import pytest

from hermes.inteligencia.sec.filings import ET, Filing


def crear_filing(forma: str, aceptado: str, items: tuple[str, ...] = (), cik: int = 1234) -> Filing:
    momento = datetime.fromisoformat(aceptado).replace(tzinfo=ET)
    return Filing(cik=cik, forma=forma, acceso=f"0000000000-{momento:%y%m%d%H%M}", fecha=momento.date(),
                  aceptado=momento, items=items, documento="doc.htm")


@pytest.fixture
def filing():
    return crear_filing


def hecho(val, end, filed, start=None):
    registro = {"val": val, "end": end, "filed": filed}
    if start:
        registro["start"] = start
    return registro


@pytest.fixture
def companyfacts():
    return {
        "facts": {
            "us-gaap": {
                "CashAndCashEquivalentsAtCarryingValue": {"units": {"USD": [
                    hecho(5_000_000, "2024-03-31", "2024-05-10"),
                    hecho(3_000_000, "2024-06-30", "2024-08-12"),
                ]}},
                "NetCashProvidedByUsedInOperatingActivities": {"units": {"USD": [
                    hecho(-3_000_000, "2024-03-31", "2024-05-10", start="2024-01-01"),
                    hecho(-6_000_000, "2024-06-30", "2024-08-12", start="2024-01-01"),
                    hecho(-3_000_000, "2024-06-30", "2024-08-12", start="2024-04-01"),
                ]}},
            },
            "dei": {
                "EntityCommonStockSharesOutstanding": {"units": {"shares": [
                    hecho(10_000_000, "2024-05-08", "2024-05-10"),
                    hecho(20_000_000, "2024-08-09", "2024-08-12"),
                ]}},
            },
        }
    }
