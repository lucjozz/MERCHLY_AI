"""Tests del calendario de temporadas (docs/004-Backend/05, sección 3)."""

from datetime import date

from app.models.organizacion import Organizacion
from app.services.organizacion import contexto_para_ia
from app.services.temporadas import TEMPORADAS, pascua, proximas_temporadas, resumen_para_ia


def test_pascua_y_fechas_variables() -> None:
    assert pascua(2026) == date(2026, 4, 5)
    assert pascua(2027) == date(2027, 3, 28)
    carnaval = next(t for t in TEMPORADAS if t.clave == "carnaval")
    assert carnaval.fecha_de(2026) == date(2026, 2, 14)  # sábado de Carnaval
    black = next(t for t in TEMPORADAS if t.clave == "black_friday")
    assert black.fecha_de(2026) == date(2026, 11, 27)
    assert black.fecha_de(2027) == date(2027, 11, 26)


def test_proximas_ordenadas_y_dentro_de_la_ventana() -> None:
    r = proximas_temporadas(date(2026, 11, 23), dias=120)
    assert [t.clave for t in r][:3] == ["black_friday", "navidad", "anio_nuevo"]
    assert all(0 <= t.dias_faltantes <= 120 for t in r)
    assert r == sorted(r, key=lambda t: t.dias_faltantes)


def test_pasa_al_anio_siguiente_y_marca_preparar_ya() -> None:
    r = {t.clave: t for t in proximas_temporadas(date(2026, 12, 26), dias=365)}
    assert r["navidad"].fecha == date(2027, 12, 25)
    assert r["anio_nuevo"].fecha == date(2027, 1, 1) and r["anio_nuevo"].preparar_ya
    assert not r["navidad"].preparar_ya
    assert r["clases"].aproximada


def test_hoy_mismo_cuenta_como_proxima() -> None:
    r = proximas_temporadas(date(2026, 5, 27), dias=0)
    assert [t.clave for t in r] == ["madre"] and r[0].dias_faltantes == 0


def test_resumen_para_ia() -> None:
    assert resumen_para_ia(date(2026, 11, 23), 2) == "Black Friday (en 4 días), Navidad (en 32 días)"


def test_contexto_de_la_ia_incluye_temporadas_solo_en_bolivia() -> None:
    bo = Organizacion(nombre="A", pais="BO")
    mx = Organizacion(nombre="B", pais="MX")
    assert "Próximas fechas comerciales en Bolivia" in contexto_para_ia(bo)
    assert "Próximas fechas comerciales en Bolivia" not in contexto_para_ia(mx)
