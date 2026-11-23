# Imagen del backend (docs/013-Seguridad/04, sección 7).
# - Multi-etapa: la imagen final no tiene pip cache ni herramientas de build.
# - psycopg[binary] trae su propia libpq: no hace falta gcc ni libpq-dev.
# - Corre como usuario sin privilegios.
# - Base fijada por digest (actualizar a propósito, no por accidente).

FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928 AS build

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Parches de seguridad del sistema base (p. ej. zlib) sin esperar a una
# nueva imagen oficial.
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 10001 merchly \
    && useradd --system --uid 10001 --gid merchly --no-create-home --shell /usr/sbin/nologin merchly

WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY --chown=root:root app ./app
COPY --chown=root:root alembic ./alembic
COPY --chown=root:root alembic.ini .
COPY --chown=root:root scripts ./scripts

USER merchly

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--no-server-header", "--no-proxy-headers"]
