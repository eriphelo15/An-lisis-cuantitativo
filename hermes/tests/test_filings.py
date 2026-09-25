from datetime import date, datetime

from hermes.inteligencia.sec.filings import ET, Categoria, clasificar, conocidos_en, parsear_aceptacion, parsear_bloque


def test_aceptacion_se_interpreta_en_hora_del_este():
    momento = parsear_aceptacion("2023-11-02T18:08:27.000Z")
    assert momento == datetime(2023, 11, 2, 18, 8, 27, tzinfo=ET)


def test_parsear_bloque_de_submissions():
    bloque = {
        "accessionNumber": ["0001-24-000001", "0001-24-000002"],
        "form": ["8-K", "424B5"],
        "filingDate": ["2024-03-01", "2024-03-05"],
        "acceptanceDateTime": ["2024-03-01T16:05:00.000Z", "2024-03-05T07:30:00.000Z"],
        "items": ["1.01,3.02", ""],
        "primaryDocument": ["ek.htm", "p.htm"],
    }
    filings = parsear_bloque(bloque, cik=320193)
    assert [f.forma for f in filings] == ["8-K", "424B5"]
    assert filings[0].items == ("1.01", "3.02")
    assert filings[1].items == ()
    assert filings[0].fecha == date(2024, 3, 1)
    assert filings[0].url == "https://www.sec.gov/Archives/edgar/data/320193/000124000001/ek.htm"


def test_parsear_bloque_sin_items():
    bloque = {"accessionNumber": ["x"], "form": ["S-3"], "filingDate": ["2024-01-02"],
              "acceptanceDateTime": ["2024-01-02T10:00:00.000Z"]}
    assert parsear_bloque(bloque, cik=1)[0].items == ()


def test_clasificar(filing):
    casos = {
        ("S-3/A", ()): {Categoria.SHELF},
        ("F-3", ()): {Categoria.SHELF},
        ("424B5", ()): {Categoria.PROSPECTO},
        ("424B3", ()): {Categoria.PROSPECTO},
        ("S-1", ()): {Categoria.S1},
        ("8-K", ("1.01", "3.02")): {Categoria.ACUERDO_FINANCIAMIENTO},
        ("8-K", ("3.01",)): {Categoria.AVISO_LISTADO},
        ("8-K", ("5.03", "9.01")): {Categoria.CAMBIO_ESTATUTOS},
        ("8-K", ("2.02",)): {Categoria.OTRO},
        ("10-Q", ()): {Categoria.FINANCIERO},
        ("4", ()): {Categoria.INSIDER},
        ("SC 13D/A", ()): {Categoria.PARTICIPACION},
        ("SCHEDULE 13G", ()): {Categoria.PARTICIPACION},
        ("RW", ()): {Categoria.RETIRO},
        ("S-8", ()): {Categoria.PLAN_EMPLEADOS},
    }
    for (forma, items), esperado in casos.items():
        assert clasificar(filing(forma, "2024-01-02T10:00:00", items)) == esperado, forma


def test_conocidos_en_excluye_el_futuro(filing):
    antes = filing("424B5", "2024-03-05T07:30:00")
    despues = filing("424B5", "2024-03-05T09:31:00")
    apertura = datetime(2024, 3, 5, 9, 30, tzinfo=ET)
    assert conocidos_en([antes, despues], apertura) == [antes]
