"""Pruebas con las APIs REALES de IA y medición de costo (docs/007-Agentes/07, sección 5).

Uso (desde la raíz del repo, con GEMINI_API_KEY y OPENAI_API_KEY en backend/.env):
    docker compose exec backend python -m scripts.probar_ia
    docker compose exec backend python -m scripts.probar_ia --categoria "mochilas antirrobo" --mercado BO

Qué hace: lista los modelos disponibles con tus claves, corre UNA investigación
(Gemini) y UNA campaña (OpenAI) por plan, y muestra tokens, tiempo y costo
estimado. No guarda nada en la base. Gasta centavos de verdad.

Los precios de PRECIOS_USD_POR_MILLON son aproximados (noviembre 2026):
verificalos en las páginas oficiales de Google y OpenAI y corregilos acá.
"""

import argparse
import asyncio
import time
from types import SimpleNamespace

from app.core.config import get_settings
from app.schemas.investigador_producto import InvestigacionInput
from app.schemas.marketing import MarketingInput
from app.services.planes import PLANES, modelo_para

# (entrada, salida) en USD por millón de tokens. Aproximados: VERIFICAR.
PRECIOS_USD_POR_MILLON: dict[str, tuple[float, float]] = {
    "gemini-2.5-flash-lite": (0.10, 0.40),
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.5-pro": (1.25, 10.00),
    "gpt-5-nano": (0.05, 0.40),
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5": (1.25, 10.00),
}
USOS_POR_MES = 60  # búsquedas y campañas de un emprendedor activo


def costo(modelo: str, entrada: int, salida: int) -> float | None:
    precio = PRECIOS_USD_POR_MILLON.get(modelo)
    if precio is None:
        return None
    return entrada / 1e6 * precio[0] + salida / 1e6 * precio[1]


def fmt_costo(valor: float | None) -> str:
    return "sin precio cargado" if valor is None else f"US$ {valor:.4f}"


async def listar_modelos() -> tuple[set[str], set[str]]:
    s = get_settings()
    gemini, openai_ = set(), set()
    if s.gemini_api_key:
        from google import genai

        cliente = genai.Client(api_key=s.gemini_api_key)
        async for m in await cliente.aio.models.list():
            nombre = (m.name or "").removeprefix("models/")
            if nombre.startswith("gemini"):
                gemini.add(nombre)
    if s.openai_api_key:
        from openai import AsyncOpenAI

        cliente = AsyncOpenAI(api_key=s.openai_api_key, timeout=20, max_retries=0)
        async for m in cliente.models.list():
            if m.id.startswith(("gpt", "o")):
                openai_.add(m.id)
    return gemini, openai_


async def probar_investigador(modelo: str, categoria: str, mercado: str):
    from app.services.proveedores.gemini import ProveedorInvestigacionGemini

    proveedor = ProveedorInvestigacionGemini(modelo=modelo)
    inicio = time.perf_counter()
    productos = await proveedor.investigar(
        InvestigacionInput(categoria=categoria, mercado_objetivo=mercado, cantidad_resultados=5)
    )
    return productos, proveedor.ultimo_uso, time.perf_counter() - inicio


async def probar_marketing(modelo: str, productos, mercado: str):
    from app.services.proveedores.marketing_openai import ProveedorMarketingOpenAI

    filas = [
        SimpleNamespace(
            nombre_producto=p.nombre_producto,
            categoria=p.categoria,
            mercado_objetivo=mercado,
            precio_sugerido_venta=p.precio_sugerido_venta,
            nivel_demanda_estimado=p.nivel_demanda_estimado.value,
            nivel_competencia_estimado=p.nivel_competencia_estimado.value,
            fuentes_evidencia=p.fuentes_evidencia,
            riesgos_identificados=p.riesgos_identificados,
        )
        for p in productos[:1]
    ]
    proveedor = ProveedorMarketingOpenAI(modelo=modelo)
    entrada = MarketingInput(
        productos_candidato_ids=["00000000-0000-4000-8000-000000000001"],
        canales_objetivo=["redes_sociales", "email"],
        idioma_destino="es",
    )
    inicio = time.perf_counter()
    resultado = await proveedor.generar_campana(entrada, filas)
    return resultado, proveedor.ultimo_uso, time.perf_counter() - inicio


async def main(categoria: str, mercado: str, planes: list[str]) -> None:
    s = get_settings()
    print("== Claves ==")
    print(f"  Gemini: {'configurada' if s.gemini_api_key else 'FALTA (GEMINI_API_KEY)'}")
    print(f"  OpenAI: {'configurada' if s.openai_api_key else 'FALTA (OPENAI_API_KEY)'}")
    gemini, openai_ = await listar_modelos()
    print(f"\n== Modelos disponibles ==\n  Gemini: {', '.join(sorted(gemini)) or '-'}\n  OpenAI: {', '.join(sorted(m for m in openai_ if m.startswith('gpt'))) or '-'}")

    filas_resumen = []
    for plan in planes:
        m_inv, m_mkt = modelo_para("investigador", plan), modelo_para("marketing", plan)
        print(f"\n== Plan {plan}: investigador={m_inv} | marketing={m_mkt} ==")
        productos = []
        if s.gemini_api_key:
            if gemini and m_inv not in gemini:
                print(f"  ⚠ {m_inv} no está disponible para tu clave de Gemini")
            try:
                productos, (ent, sal), seg = await probar_investigador(m_inv, categoria, mercado)
                c = costo(m_inv, ent, sal)
                print(f"  Investigador: {len(productos)} productos en {seg:.1f}s | tokens {ent} entrada / {sal} salida | {fmt_costo(c)}")
                for p in productos[:5]:
                    print(f"    - {p.nombre_producto} | demanda {p.nivel_demanda_estimado.value} | evidencia: {', '.join(p.fuentes_evidencia[:2]) or 'ninguna'}")
                filas_resumen.append((plan, "investigador", m_inv, c, seg))
            except Exception as error:  # noqa: BLE001 - es un script de diagnóstico
                print(f"  Investigador FALLÓ: {error}")
        if s.openai_api_key and productos:
            if openai_ and m_mkt not in openai_:
                print(f"  ⚠ {m_mkt} no está disponible para tu clave de OpenAI")
            try:
                r, (ent, sal), seg = await probar_marketing(m_mkt, productos, mercado)
                c = costo(m_mkt, ent, sal)
                print(f"  Marketing: {len(r.angulos_de_campana)} ángulos en {seg:.1f}s | tokens {ent} entrada / {sal} salida | {fmt_costo(c)}")
                for canal, variantes in r.copy_por_canal.items():
                    print(f"    [{canal.value}] {variantes[0].titulo if variantes else '-'}")
                filas_resumen.append((plan, "marketing", m_mkt, c, seg))
            except Exception as error:  # noqa: BLE001
                print(f"  Marketing FALLÓ: {error}")

    print("\n== Resumen de costos ==")
    for plan in planes:
        costos = [c for (p, _, _, c, _) in filas_resumen if p == plan and c is not None]
        if costos:
            por_uso = sum(costos)
            print(f"  {plan:12s} búsqueda + campaña: US$ {por_uso:.4f} | {USOS_POR_MES} de cada por mes: US$ {por_uso * USOS_POR_MES:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--categoria", default="linternas recargables")
    parser.add_argument("--mercado", default="BO")
    parser.add_argument("--plan", choices=PLANES, help="probar un solo plan (por defecto, los tres)")
    args = parser.parse_args()
    asyncio.run(main(args.categoria, args.mercado, [args.plan] if args.plan else list(PLANES)))
