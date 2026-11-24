"""Tests unitarios del inventario: separación privado/público, fotos e importación (docs/007-Agentes/08)."""

import base64
import io
import zipfile
from decimal import Decimal

import pytest
from openpyxl import Workbook
from PIL import Image

from app.schemas.inventario import ItemCatalogoPublico, ProductoInventarioEntrada
from app.services.imagenes import ImagenInvalidaError, decodificar_base64, recodificar
from app.services.importar_inventario import (
    ArchivoInvalidoError,
    detectar_columnas,
    parsear_numero,
    vista_previa,
)

# ------------------------------------------------------------ dos catálogos


def test_el_catalogo_publico_nunca_tiene_campos_privados() -> None:
    """La IA lee SOLO este schema: si alguien le agrega un campo privado, esto falla."""
    publicos = set(ItemCatalogoPublico.model_fields)
    privados = {"costo_unitario", "gastos_unitarios", "proveedor", "notas_internas", "stock", "stock_reservado",
                "margen_unitario", "sku", "origen"}
    assert publicos == {"id", "nombre", "descripcion", "especificaciones", "precio_venta", "disponibles", "foto_ids"}
    assert not publicos & privados


def test_entrada_rechaza_campos_del_sistema() -> None:
    with pytest.raises(ValueError):
        ProductoInventarioEntrada(nombre="x", organizacion_id="otra")  # mass assignment
    with pytest.raises(ValueError):
        ProductoInventarioEntrada(nombre="x", stock_reservado=5)  # lo maneja solo el sistema
    with pytest.raises(ValueError):
        ProductoInventarioEntrada(nombre="x", stock=-1)
    with pytest.raises(ValueError):
        ProductoInventarioEntrada(nombre="x", precio_venta=Decimal("-1"))
    with pytest.raises(ValueError):
        ProductoInventarioEntrada(nombre="x", especificaciones={f"k{i}": "v" for i in range(21)})


# ------------------------------------------------------------ fotos


def _imagen(formato: str, tamano=(64, 48), exif: bool = False) -> bytes:
    salida = io.BytesIO()
    imagen = Image.new("RGB", tamano, (200, 30, 30))
    extra = {}
    if exif:
        datos_exif = Image.Exif()
        datos_exif[0x0110] = "Celular secreto"  # Model
        extra["exif"] = datos_exif.tobytes()
    imagen.save(salida, format=formato, **extra)
    return salida.getvalue()


def test_foto_se_recodifica_a_webp_sin_metadatos() -> None:
    resultado = recodificar(_imagen("JPEG", exif=True))
    with Image.open(io.BytesIO(resultado)) as imagen:
        assert imagen.format == "WEBP"
        assert not imagen.getexif()
    assert b"Celular secreto" not in resultado


def test_foto_grande_se_achica() -> None:
    with Image.open(io.BytesIO(recodificar(_imagen("PNG", tamano=(3000, 1000))))) as imagen:
        assert max(imagen.size) == 1600


@pytest.mark.parametrize("datos", [b"GIF89a" + b"0" * 200, b"<svg onload=alert(1)>" + b" " * 200, b"%PDF-1.4" + b"0" * 200])
def test_foto_rechaza_lo_que_no_es_jpg_png_webp(datos: bytes) -> None:
    with pytest.raises(ImagenInvalidaError):
        recodificar(datos)


def test_foto_rechaza_gif_real() -> None:
    salida = io.BytesIO()
    Image.new("P", (10, 10)).save(salida, format="GIF")
    with pytest.raises(ImagenInvalidaError):
        recodificar(salida.getvalue())


def test_base64_roto_o_enorme() -> None:
    with pytest.raises(ImagenInvalidaError):
        decodificar_base64("esto no es base64!!", 1000)
    with pytest.raises(ImagenInvalidaError):
        decodificar_base64(base64.b64encode(b"x" * 2000).decode(), 1000)
    assert decodificar_base64("data:image/png;base64," + base64.b64encode(b"hola").decode(), 1000) == b"hola"


# ------------------------------------------------------------ importar


@pytest.mark.parametrize(
    "crudo, esperado",
    [
        ("Bs 1.250,50", Decimal("1250.50")), ("1,250.50", Decimal("1250.50")), ("12,5", Decimal("12.50")),
        ("1,250", Decimal("1250.00")), ("120", Decimal("120.00")), (99.9, Decimal("99.90")),
        ("1.250.000", Decimal("1250000.00")), ("", None), ("consultar", None), (None, None),
    ],
)
def test_parsear_numero(crudo, esperado) -> None:
    assert parsear_numero(crudo) == esperado


def test_detectar_columnas_con_sinonimos_y_tildes() -> None:
    cols = detectar_columnas(["Código", "Artículo", "Precio de Venta", "Costo", "Cantidad"])
    assert cols == {"nombre": 1, "sku": 0, "descripcion": None, "precio_venta": 2, "costo_unitario": 3, "stock": 4}


def test_csv_con_punto_y_coma_y_problemas_marcados() -> None:
    csv = "Producto;Precio;Stock\nTaladro 800W;Bs 450,00;5\nLinterna;consultar;dos\n;10;1\n".encode("latin-1")
    r = vista_previa("lista.csv", csv)
    assert r.formato == "csv" and r.columnas["precio_venta"] == "Precio"
    assert [f.nombre for f in r.filas] == ["Taladro 800W", "Linterna"]
    assert r.filas[0].precio_venta == Decimal("450.00") and r.filas[0].stock == 5 and r.filas[0].problemas == []
    assert r.filas[1].precio_venta is None and r.filas[1].stock is None and len(r.filas[1].problemas) == 2
    assert r.descartadas == 1  # fila sin nombre: nunca se inventa


def _xlsx(filas: list[list]) -> bytes:
    libro = Workbook()
    hoja = libro.active
    for fila in filas:
        hoja.append(fila)
    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


def test_excel_se_lee_sin_formulas() -> None:
    datos = _xlsx([["Nombre", "PVP", "Existencias"], ["Carpa 4p", 899.5, 3], ["Mochila", "=1+1", 2]])
    r = vista_previa("catalogo.xlsx", datos)
    assert r.formato == "xlsx" and len(r.filas) == 2
    assert r.filas[0].precio_venta == Decimal("899.50") and r.filas[0].stock == 3
    assert r.filas[1].precio_venta is None and r.filas[1].problemas  # la fórmula no se ejecuta


def test_excel_con_macros_se_rechaza() -> None:
    datos = io.BytesIO(_xlsx([["Nombre"], ["x"]]))
    with zipfile.ZipFile(datos, "a") as z:
        z.writestr("xl/vbaProject.bin", b"macro")
    with pytest.raises(ArchivoInvalidoError, match="macros"):
        vista_previa("c.xlsx", datos.getvalue())


def test_zip_bomb_se_rechaza() -> None:
    datos = io.BytesIO()
    with zipfile.ZipFile(datos, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("xl/bomba.xml", b"0" * (40 * 1024 * 1024))
    with pytest.raises(ArchivoInvalidoError, match="grande"):
        vista_previa("c.xlsx", datos.getvalue())


@pytest.mark.parametrize(
    "nombre, datos, mensaje",
    [
        ("c.pdf", b"%PDF-1.7 ...", "PDF"),
        ("c.xls", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"0" * 50, "viejo"),
        ("c.jpg", b"\xff\xd8\xff" + b"0" * 50, "fotos"),
    ],
)
def test_otros_formatos_dan_mensaje_claro(nombre, datos, mensaje) -> None:
    with pytest.raises(ArchivoInvalidoError, match=mensaje):
        vista_previa(nombre, datos)


def test_sin_columna_de_nombre_o_sin_filas() -> None:
    with pytest.raises(ArchivoInvalidoError, match="nombre"):
        vista_previa("a.csv", b"precio,stock\n10,1\n")
    with pytest.raises(ArchivoInvalidoError, match="filas"):
        vista_previa("a.csv", b"producto,precio\n")


def test_tope_de_filas() -> None:
    csv = "producto,precio\n" + "".join(f"P{i},{i}\n" for i in range(600))
    r = vista_previa("a.csv", csv.encode())
    assert len(r.filas) == 500 and r.descartadas == 100
