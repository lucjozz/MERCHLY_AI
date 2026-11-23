# Imagen del frontend (Next.js) para hostings que corren Docker (DEC-036).
# En Render se usa el runtime de Node (render.yaml); esto es para otros proveedores.
# - Multi-etapa: dependencias de build fuera de la imagen final.
# - Corre como usuario sin privilegios.
# Las variables NEXT_PUBLIC_* se fijan al construir (son públicas por definición).

FROM node:24-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG NEXT_PUBLIC_GOOGLE_CLIENT_ID=""
ARG NEXT_PUBLIC_SOPORTE_WHATSAPP=""
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build && npm prune --omit=dev

FROM node:24-slim
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000
COPY --from=build --chown=node:node /app/package.json ./
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/.next ./.next
COPY --from=build --chown=node:node /app/public ./public
COPY --from=build --chown=node:node /app/next.config.ts ./
USER node
EXPOSE 3000
CMD ["npm", "run", "start"]
