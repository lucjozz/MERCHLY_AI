"""Importar un catálogo existente: Excel y CSV (docs/007-Agentes/08, sección 3.3). Sin FastAPI.

Determinístico (sin IA). Nunca guarda: devuelve una vista previa que el dueño
revisa y confirma. Los otros formatos (PDF, Word, fotos) se leen con IA en la
fase A2.

Defensas: tope de tamaño y de filas, Excel abierto sin fórmulas ni macros
(``read_only`` + ``data_only``), control del tamaño descomprimido del .xlsx
(zip bomb) y XML con ``defusedxml`` (openpyxl lo usa si está instalado).
"""

import csv
import io
import re
import unicodedata
import zipfile
from decimal import Decimal, InvalidOperation

from openpyxl import load_workbook

from app.schemas.inventario import FilaImportada, ImportarVistaPrevia

MAX_BYTES_ARCHIVO = 750 * 1024
MAX_BYTES_DESCOMPRIMIDO = 30 * 1024 * 1024
MAX_FILAS = 500
MAX_COLUMNAS = 40

# campo → palabras con las que suele venir la columna (sin tildes, en minúscula)
SINONIMOS: dict[str, tuple[str, ...]] = {
    "nombre": ("nombre", "producto", "articulo", "item", "descripcion del producto", "detalle"),
    "sku": ("sku", "codigo", "cod", "referencia", "ref"),
    "descripcion": ("descripcion", "caracteristicas", "detalle largo"),
    "precio_venta": ("precio venta", "precio de venta", "pvp", "precio", "precio publico", "venta"),
    "costo_unitario": ("costo", "precio compra", "precio de compra", "costo unitario", "compra"),
    "stock": ("stock", "cantidad", "existencia", "existencias", "unidades", "cant", "disponible"),
}


class ArchivoInvalidoError(Exception):
    """Mensaje apto para mostrar al usuario."""


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", sin_tildes.lower()).strip()


def detectar_columnas(encabezados: list[str]) -> dict[str, int | None]:
    """Elige la columna para cada campo: primero coincidencia exacta, después parcial."""
    normalizados = [_normalizar(e) for e in encabezados]
    elegidas: dict[str, int | None] = {}
    usadas: set[int] = set()
    for exacta in (True, False):
        for campo, palabras in SINONIMOS.items():
            if elegidas.get(campo) is not None:
                continue
            for palabra in palabras:
                indice = next(
                    (
                        i for i, e in enumerate(normalizados)
                        if i not in usadas and e and (e == palabra if exacta else palabra in e)
                    ),
                    None,
                )
                if indice is not None:
                    elegidas[campo] = indice
                    usadas.add(indice)
                    break
    return {campo: elegidas.get(campo) for campo in SINONIMOS}


def parsear_numero(valor) -> Decimal | None:
    """'Bs 1.250,50' → 1250.50 · '1,250.50' → 1250.50 · '12,5' → 12.5. None si no es un número."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, (int, float, Decimal)) and not isinstance(valor, bool):
        try:
            return Decimal(str(valor)).quantize(Decimal("0.01"))
        except InvalidOperation:
            return None
    texto = re.sub(r"[^0-9,.\-]", "", str(valor))
    if not texto or texto in "-.,":
        return None
    if "," in texto and "." in texto:
        decimal_es_coma = texto.rfind(",") > texto.rfind(".")
        texto = texto.replace(".", "").replace(",", ".") if decimal_es_coma else texto.replace(",", "")
    elif "," in texto:
        partes = texto.split(",")
        # "1,250" (miles) vs "12,50" (decimales): 3 dígitos después de cada coma = miles
        es_miles = len(partes) > 1 and all(len(p) == 3 for p in partes[1:]) and len(partes[0]) <= 3
        texto = texto.replace(",", "") if es_miles else texto.replace(",", ".")
    elif texto.count(".") > 1:
        texto = texto.replace(".", "")  # "1.250.000"
    try:
        return Decimal(texto).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def _leer_xlsx(datos: bytes) -> tuple[list[list], int]:
    try:
        with zipfile.ZipFile(io.BytesIO(datos)) as z:
            if sum(i.file_size for i in z.infolist()) > MAX_BYTES_DESCOMPRIMIDO:
                raise ArchivoInvalidoError("El Excel es demasiado grande por dentro.")
            if any(n.lower().endswith("vbaproject.bin") for n in z.namelist()):
                raise ArchivoInvalidoError("El Excel tiene macros. Guardalo como .xlsx sin macros y probá de nuevo.")
        libro = load_workbook(io.BytesIO(datos), read_only=True, data_only=True)
    except ArchivoInvalidoError:
        raise
    except Exception as error:  # noqa: BLE001 - cualquier archivo roto es un error del usuario
        raise ArchivoInvalidoError("No pudimos abrir el Excel. ¿Está guardado como .xlsx?") from error
    try:
        hoja = libro.worksheets[0]
        filas, sobrantes = [], 0
        for fila in hoja.iter_rows(values_only=True, max_col=MAX_COLUMNAS):
            if len(filas) <= MAX_FILAS:
                filas.append(list(fila))
            elif any(c not in (None, "") for c in fila):
                sobrantes += 1  # se cuentan para avisarle al dueño, no se guardan
        return filas, sobrantes
    finally:
        libro.close()


def _leer_csv(datos: bytes) -> tuple[list[list], int]:
    for codificacion in ("utf-8-sig", "latin-1"):
        try:
            texto = datos.decode(codificacion)
            break
        except UnicodeDecodeError:
            continue
    muestra = texto[:4096]
    try:
        dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t|")
    except csv.Error:
        dialecto = csv.excel
    filas, sobrantes = [], 0
    for fila in csv.reader(io.StringIO(texto), dialecto):
        if len(filas) <= MAX_FILAS:
            filas.append(fila[:MAX_COLUMNAS])
        elif any(c.strip() for c in fila):
            sobrantes += 1
    return filas, sobrantes


def detectar_formato(nombre_archivo: str, datos: bytes) -> str:
    nombre = nombre_archivo.lower()
    if datos[:4] == b"PK\x03\x04":
        if nombre.endswith(".docx"):
            return "word"
        return "xlsx"
    if datos[:5] == b"%PDF-":
        return "pdf"
    if datos[:3] == b"\xff\xd8\xff" or datos[:8] == b"\x89PNG\r\n\x1a\n" or datos[8:12] == b"WEBP":
        return "imagen"
    if datos[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "xls"
    if nombre.endswith((".csv", ".txt", ".tsv")) or b"\x00" not in datos[:2048]:
        return "csv"
    return "desconocido"


MENSAJE_FORMATO = {
    "pdf": "Los catálogos en PDF los va a leer la IA en la próxima versión. Por ahora subí un Excel (.xlsx) o un CSV.",
    "word": "Los documentos de Word los va a leer la IA en la próxima versión. Por ahora subí un Excel (.xlsx) o un CSV.",
    "imagen": "Las fotos de catálogos las va a leer la IA en la próxima versión. Por ahora subí un Excel (.xlsx) o un CSV.",
    "xls": "Ese es un Excel viejo (.xls). Abrilo y guardalo como .xlsx, o exportalo como CSV.",
    "desconocido": "No reconocemos ese archivo. Subí un Excel (.xlsx) o un CSV.",
}


def _texto(valor, largo: int) -> str | None:
    if valor is None:
        return None
    texto = re.sub(r"\s+", " ", str(valor)).strip()
    return texto[:largo] or None


def vista_previa(nombre_archivo: str, datos: bytes) -> ImportarVistaPrevia:
    if len(datos) > MAX_BYTES_ARCHIVO:
        raise ArchivoInvalidoError("El archivo es demasiado grande (máximo 750 KB).")
    formato = detectar_formato(nombre_archivo, datos)
    if formato not in ("xlsx", "csv"):
        raise ArchivoInvalidoError(MENSAJE_FORMATO[formato])
    filas, sobrantes = _leer_xlsx(datos) if formato == "xlsx" else _leer_csv(datos)
    filas = [f for f in filas if any(c not in (None, "") for c in f)]
    if len(filas) < 2:
        raise ArchivoInvalidoError("El archivo no tiene filas de productos (la primera fila tiene que ser el encabezado).")
    encabezados = [str(c or "").strip() for c in filas[0]]
    columnas = detectar_columnas(encabezados)
    if columnas["nombre"] is None:
        raise ArchivoInvalidoError("No encontramos la columna con el nombre del producto (por ejemplo: «Producto» o «Nombre»).")

    def celda(fila: list, campo: str):
        i = columnas[campo]
        return fila[i] if i is not None and i < len(fila) else None

    resultado: list[FilaImportada] = []
    descartadas = sobrantes
    for numero, fila in enumerate(filas[1:], start=2):
        if len(resultado) >= MAX_FILAS:
            descartadas += 1
            continue
        nombre = _texto(celda(fila, "nombre"), 200)
        if not nombre:
            descartadas += 1
            continue
        problemas = []
        precios = {}
        for campo in ("precio_venta", "costo_unitario"):
            crudo = celda(fila, campo)
            valor = parsear_numero(crudo)
            if crudo not in (None, "") and (valor is None or valor < 0):
                problemas.append(f"No entendimos el {'precio' if campo == 'precio_venta' else 'costo'}: «{_texto(crudo, 30)}»")
                valor = None
            precios[campo] = valor
        crudo_stock = celda(fila, "stock")
        stock_decimal = parsear_numero(crudo_stock)
        stock = None
        if stock_decimal is not None and stock_decimal >= 0 and stock_decimal == stock_decimal.to_integral_value():
            stock = int(stock_decimal)
        elif crudo_stock not in (None, ""):
            problemas.append(f"No entendimos la cantidad: «{_texto(crudo_stock, 30)}»")
        if precios["precio_venta"] is None and not problemas:
            problemas.append("Sin precio de venta")
        resultado.append(
            FilaImportada(
                fila=numero, nombre=nombre, sku=_texto(celda(fila, "sku"), 60),
                descripcion=_texto(celda(fila, "descripcion"), 2000) if columnas["descripcion"] != columnas["nombre"] else None,
                precio_venta=precios["precio_venta"], costo_unitario=precios["costo_unitario"], stock=stock,
                problemas=problemas,
            )
        )
    return ImportarVistaPrevia(
        formato=formato,
        columnas={campo: (encabezados[i] if i is not None else None) for campo, i in columnas.items()},
        filas=resultado,
        descartadas=descartadas,
    )
