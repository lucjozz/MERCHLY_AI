"""Base de seguridad para los webhooks de Meta (Fase B), docs/007-Agentes/09, sección 3.1."""

import hashlib
import hmac
import uuid

import pytest

from app.core.cifrado import CifradoInvalidoError
from app.services.canales import seguridad_webhook as w
from app.tests.conftest import RedisFalso

SECRETO = "app-secret-de-prueba"
CUERPO = b'{"entry":[{"changes":[{"value":{"messages":[{"id":"wamid.1","text":{"body":"hola"}}]}}]}]}'


def _firma(cuerpo: bytes, secreto: str = SECRETO) -> str:
    return "sha256=" + hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()


def test_firma_valida_e_invalida() -> None:
    assert w.firma_valida(CUERPO, _firma(CUERPO), SECRETO)
    assert not w.firma_valida(CUERPO + b" ", _firma(CUERPO), SECRETO)  # cuerpo alterado
    assert not w.firma_valida(CUERPO, _firma(CUERPO, "otro"), SECRETO)  # firmado con otra clave
    assert not w.firma_valida(CUERPO, _firma(CUERPO).replace("sha256=", "sha1="), SECRETO)
    for cabecera, secreto in ((None, SECRETO), ("", SECRETO), (_firma(CUERPO), None), (_firma(CUERPO), "")):
        assert not w.firma_valida(CUERPO, cabecera, secreto)  # falla cerrado


def test_suscripcion() -> None:
    assert w.responder_suscripcion("subscribe", "tok", "12345", "tok") == "12345"
    assert w.responder_suscripcion("subscribe", "malo", "12345", "tok") is None
    assert w.responder_suscripcion("unsubscribe", "tok", "12345", "tok") is None
    assert w.responder_suscripcion("subscribe", "tok", "12345", None) is None  # sin configurar: nunca acepta


async def test_idempotencia() -> None:
    redis = RedisFalso()
    assert await w.es_nuevo(redis, "whatsapp", "wamid.1") is True
    assert await w.es_nuevo(redis, "whatsapp", "wamid.1") is False  # reintento de Meta
    assert await w.es_nuevo(redis, "instagram", "wamid.1") is True  # otro canal, otro espacio


def test_mensajes_viejos_se_descartan() -> None:
    ahora = 1_800_000_000
    assert w.es_reciente(ahora - 60, ahora)
    assert not w.es_reciente(ahora - 2 * 24 * 3600, ahora)
    assert not w.es_reciente(ahora + 3600, ahora)  # del "futuro"
    assert not w.es_reciente("no-es-numero", ahora) and not w.es_reciente(None, ahora)


def test_tokens_cifrados_y_atados_a_su_dueno() -> None:
    org_a, org_b = uuid.uuid4(), uuid.uuid4()
    valor = w.cifrar_token(org_a, "whatsapp", "EAAG-token-secreto")
    assert "EAAG" not in valor
    assert w.descifrar_token(org_a, "whatsapp", valor) == "EAAG-token-secreto"
    with pytest.raises(CifradoInvalidoError):
        w.descifrar_token(org_b, "whatsapp", valor)  # copiado a otra organización
    with pytest.raises(CifradoInvalidoError):
        w.descifrar_token(org_a, "instagram", valor)  # usado para otro canal
