# ── Etapa 1: compilar Angular ──────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts

COPY . .
RUN npx ng build --configuration production

# ── Etapa 2: servir con nginx ───────────────────────────────────────────────
FROM nginx:alpine

COPY --from=builder /app/dist/sisa-frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
