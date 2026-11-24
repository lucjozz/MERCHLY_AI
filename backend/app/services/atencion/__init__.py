"""Agente de Atención al Cliente y sus sub-agentes (docs/007-Agentes/09). Sin FastAPI.

* ``orquestador``: agente principal; en cada mensaje llama solo a los sub-agentes que hacen falta.
* ``stock``: Sub-agente Catálogo/Stock (busca en el catálogo público).
* ``envios``: Sub-agente Envíos (tarifas por zona; Yango en Fase B).
* ``venta``: Sub-agente Venta (pedido, reserva, QR, pago informado; el vendedor confirma).
* ``conversaciones``: mensajes y derivación a una persona.
* ``configuracion``: lo que controla el dueño (encendido, completar ventas, QR, zonas).

Los módulos se importan cuando se usan: no hay procesos de fondo.
"""
