"""Abstract research provider for the Agente Investigador de Producto.

The agent's technical contract (``docs/007-Agentes/03-...``, sección 1)
assigns "Gemini" as the current provider (per
``docs/100-Organizacion/06-Agentes-IA.md``). This abstraction exists so
that the actual provider (a real Gemini integration, a different LLM, or
a combination with web search) can be swapped without touching the
agent's orchestration logic — coherent with DEC-007 (proveedores
intercambiables por rol, no acoplados al rol en sí).
"""

from abc import ABC, abstractmethod

from app.schemas.investigador_producto import InvestigacionInput, ProductoCandidatoOutput


class ProveedorInvestigacionError(Exception):
    """Raised when a research provider fails to complete a request."""


class ProveedorInvestigacion(ABC):
    """Port that any product-research provider must implement."""

    @abstractmethod
    async def investigar(
        self, entrada: InvestigacionInput
    ) -> list[ProductoCandidatoOutput]:
        """Return candidate products for the given research input.

        Args:
            entrada: validated research request.

        Returns:
            list[ProductoCandidatoOutput]: candidate products found. May be
            shorter than ``entrada.cantidad_resultados`` if fewer viable
            candidates exist; must never fabricate results to fill quota.

        Raises:
            ProveedorInvestigacionError: if the provider cannot complete
            the request (network failure, quota exhausted, etc.). The
            caller (``AgenteInvestigadorProducto``) is responsible for
            retry policy per el contrato, sección 8.
        """
        raise NotImplementedError
