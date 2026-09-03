"""Tests para el modelo DecisionRecord y su conversión a DecisionOutput.

Estos tests existen específicamente para cubrir el bug corregido en
DEC-030: antes de esta corrección, ``DecisionRecord`` no tenía las
relaciones ORM hacia ``DecisionContext`` ni ``DecisionEvidence``. Eso no
rompía la escritura (los datos sí se guardaban en sus tablas), pero
hacía que ``context_data`` y ``evidencias`` salieran siempre vacíos en
la respuesta de la API — sin ningún error visible, porque Pydantic
usaba silenciosamente los valores por defecto de esos campos.

No requieren una base de datos real: se arman los objetos en memoria y
se asignan las relaciones directamente, algo que solo es posible si el
modelo las declara.
"""

import uuid
from datetime import datetime, timezone

from app.models.decisiones import DecisionContext, DecisionEvidence, DecisionRecord
from app.services.registrar_decision import _a_decision_output


def _decision_base() -> DecisionRecord:
    return DecisionRecord(
        id=uuid.uuid4(),
        decision_type="product_selection",
        entity_type="product_candidate",
        entity_id=uuid.uuid4(),
        action="approve",
        user_id="lucas",
        reason="Buen margen y demanda alta.",
        creado_en=datetime.now(timezone.utc),
    )


def test_decision_record_tiene_relacion_contexto() -> None:
    """Antes de DEC-030 esto no existía como atributo del modelo."""
    assert hasattr(DecisionRecord, "contexto")


def test_decision_record_tiene_relacion_evidencias() -> None:
    """Antes de DEC-030 esto no existía como atributo del modelo."""
    assert hasattr(DecisionRecord, "evidencias")


def test_a_decision_output_incluye_context_data_guardado() -> None:
    decision = _decision_base()
    decision.contexto = DecisionContext(
        id=uuid.uuid4(),
        decision_id=decision.id,
        context_data={"margen": 0.35, "demanda": "alta"},
    )
    decision.evidencias = []

    salida = _a_decision_output(decision)

    assert salida.context_data == {"margen": 0.35, "demanda": "alta"}


def test_a_decision_output_incluye_evidencias_guardadas() -> None:
    decision = _decision_base()
    decision.contexto = None
    decision.evidencias = [
        DecisionEvidence(
            id=uuid.uuid4(),
            decision_id=decision.id,
            source_type="market_research",
            source_url="https://ejemplo.test/informe",
            source_title="Informe de mercado",
            evidence="Demanda creciente en el segmento.",
        )
    ]

    salida = _a_decision_output(decision)

    assert len(salida.evidencias) == 1
    assert salida.evidencias[0].source_type == "market_research"
    assert salida.evidencias[0].evidence == "Demanda creciente en el segmento."


def test_a_decision_output_sin_contexto_ni_evidencias_no_falla() -> None:
    decision = _decision_base()
    decision.contexto = None
    decision.evidencias = []

    salida = _a_decision_output(decision)

    assert salida.context_data is None
    assert salida.evidencias == []
