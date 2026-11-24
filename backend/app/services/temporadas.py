"""Calendario de temporadas comerciales de Bolivia (docs/004-Backend/05, sección 3). Sin FastAPI.

Datos fijos en el código (no hay nada que guardar ni configurar). Carnaval se
calcula a partir de la Pascua y Black Friday es el cuarto viernes de
noviembre. Las fechas que cambian cada año por resolución del gobierno se
marcan como aproximadas.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta

ANTICIPACION_POR_DEFECTO = 45  # días: importar por courier tarda varias semanas


def pascua(anio: int) -> date:
    """Domingo de Pascua (algoritmo anónimo gregoriano)."""
    a, b, c = anio % 19, anio // 100, anio % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741 - nombre del algoritmo
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return date(anio, mes, dia)


def _carnaval(anio: int) -> date:
    return pascua(anio) - timedelta(days=50)  # sábado de Carnaval


def _black_friday(anio: int) -> date:
    primero = date(anio, 11, 1)
    primer_viernes = primero + timedelta(days=(4 - primero.weekday()) % 7)
    return primer_viernes + timedelta(weeks=3)


def _fija(mes: int, dia: int) -> Callable[[int], date]:
    return lambda anio: date(anio, mes, dia)


@dataclass(frozen=True)
class Temporada:
    clave: str
    nombre: str
    fecha_de: Callable[[int], date]
    ideas: tuple[str, ...]
    anticipacion_dias: int = ANTICIPACION_POR_DEFECTO
    aproximada: bool = False


TEMPORADAS: tuple[Temporada, ...] = (
    Temporada("anio_nuevo", "Año Nuevo", _fija(1, 1), ("cotillón y decoración", "ropa amarilla", "luces led"), 30),
    Temporada("alasitas", "Alasitas", _fija(1, 24), ("miniaturas", "artesanía", "billetes de alasita"), 30),
    Temporada("clases", "Regreso a clases", _fija(2, 3), ("mochilas escolares", "útiles escolares", "loncheras y termos"), 45, True),
    Temporada("san_valentin", "San Valentín", _fija(2, 14), ("regalos para pareja", "peluches", "joyería de fantasía")),
    Temporada("carnaval", "Carnaval", _carnaval, ("disfraces", "espuma y globos de agua", "ponchos impermeables")),
    Temporada("padre", "Día del Padre", _fija(3, 19), ("relojes", "billeteras de cuero", "herramientas")),
    Temporada("nino", "Día del Niño", _fija(4, 12), ("juguetes", "juegos didácticos", "ropa infantil")),
    Temporada("madre", "Día de la Madre", _fija(5, 27), ("artículos de cocina", "cosméticos", "carteras")),
    Temporada("anio_andino", "Año Nuevo Andino e invierno", _fija(6, 21), ("ropa de abrigo", "calefactores", "frazadas")),
    Temporada("estudiante", "Día del Estudiante y de la Primavera", _fija(9, 21), ("regalos para amigos", "accesorios de moda", "flores artificiales")),
    Temporada("mujer", "Día de la Mujer Boliviana", _fija(10, 11), ("cosméticos", "accesorios", "perfumes")),
    Temporada("todos_santos", "Todos Santos", _fija(11, 2), ("moldes para t'antawawas", "flores artificiales", "velas")),
    Temporada("black_friday", "Black Friday", _black_friday, ("electrónica", "audífonos", "accesorios para celular")),
    Temporada("navidad", "Navidad", _fija(12, 25), ("juguetes", "decoración navideña", "regalos personalizados"), 60),
)


@dataclass(frozen=True)
class TemporadaProxima:
    clave: str
    nombre: str
    fecha: date
    dias_faltantes: int
    anticipacion_dias: int
    preparar_ya: bool
    aproximada: bool
    ideas: tuple[str, ...]


def proximas_temporadas(hoy: date, dias: int = 120) -> list[TemporadaProxima]:
    """Temporadas desde hoy hasta ``dias`` días adelante, de la más cercana a la más lejana."""
    resultado = []
    for t in TEMPORADAS:
        fecha = t.fecha_de(hoy.year)
        if fecha < hoy:
            fecha = t.fecha_de(hoy.year + 1)
        faltan = (fecha - hoy).days
        if faltan <= dias:
            resultado.append(
                TemporadaProxima(
                    clave=t.clave,
                    nombre=t.nombre,
                    fecha=fecha,
                    dias_faltantes=faltan,
                    anticipacion_dias=t.anticipacion_dias,
                    preparar_ya=faltan <= t.anticipacion_dias,
                    aproximada=t.aproximada,
                    ideas=t.ideas,
                )
            )
    return sorted(resultado, key=lambda t: t.dias_faltantes)


def resumen_para_ia(hoy: date, cantidad: int = 3) -> str:
    """Texto corto para el contexto del Investigador: 'Navidad (en 32 días), ...'."""
    return ", ".join(f"{t.nombre} (en {t.dias_faltantes} días)" for t in proximas_temporadas(hoy)[:cantidad])
