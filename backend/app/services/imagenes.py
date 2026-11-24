"""Validación y re-codificación de imágenes subidas (docs/007-Agentes/08, sección 2.1). Sin FastAPI.

* El tipo se decide por los bytes (Pillow), no por la extensión ni el MIME del cliente.
* Solo JPEG, PNG y WebP. Tope de píxeles contra "bombas de descompresión".
* Se re-codifica a WebP sin metadatos (borra EXIF/GPS y cualquier contenido extra).
"""

import base64
import binascii
import io
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

FORMATOS_PERMITIDOS = {"JPEG", "PNG", "WEBP"}
MAX_BYTES_ENTRADA = 750 * 1024
MAX_PIXELES = 40_000_000
LADO_MAXIMO = 1600
CALIDAD_WEBP = 82


class ImagenInvalidaError(Exception):
    """Mensaje apto para mostrar al usuario."""


def decodificar_base64(texto: str, max_bytes: int) -> bytes:
    if "," in texto[:100] and texto.startswith("data:"):
        texto = texto.split(",", 1)[1]  # acepta "data:image/jpeg;base64,..."
    try:
        datos = base64.b64decode(texto, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ImagenInvalidaError("El archivo llegó dañado. Probá subirlo de nuevo.") from error
    if not datos:
        raise ImagenInvalidaError("El archivo está vacío.")
    if len(datos) > max_bytes:
        raise ImagenInvalidaError("El archivo es demasiado grande.")
    return datos


def recodificar(datos: bytes, formato: str = "WEBP", lado_maximo: int = LADO_MAXIMO) -> bytes:
    """Devuelve la imagen re-codificada y limpia (WebP por defecto; PNG sin pérdida para QR)."""
    if len(datos) > MAX_BYTES_ENTRADA:
        raise ImagenInvalidaError("La foto es demasiado grande (máximo 750 KB después de achicarla).")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(datos)) as imagen:
                if imagen.format not in FORMATOS_PERMITIDOS:
                    raise ImagenInvalidaError("Solo se aceptan fotos JPG, PNG o WebP.")
                if imagen.width * imagen.height > MAX_PIXELES:
                    raise ImagenInvalidaError("La foto tiene demasiados píxeles.")
                imagen.load()
                imagen = ImageOps.exif_transpose(imagen)  # respeta la orientación del celular
                imagen = imagen.convert("RGBA" if imagen.mode in ("RGBA", "LA", "P") else "RGB")
                imagen.thumbnail((lado_maximo, lado_maximo))
                salida = io.BytesIO()
                if formato == "PNG":
                    imagen.save(salida, format="PNG", optimize=True)
                else:
                    imagen.save(salida, format="WEBP", quality=CALIDAD_WEBP, method=4)
                return salida.getvalue()
    except ImagenInvalidaError:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError, Image.DecompressionBombWarning, OSError, ValueError) as error:
        raise ImagenInvalidaError("No pudimos leer la foto. Probá con un JPG o PNG.") from error
