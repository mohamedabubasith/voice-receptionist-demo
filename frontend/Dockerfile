# ── Build stage ──────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

# VITE_* vars are inlined at build time — pass them as build args in Coolify
ARG VITE_LIVEKIT_URL
ARG VITE_LIVEKIT_API_KEY
ARG VITE_LIVEKIT_API_SECRET
ENV VITE_LIVEKIT_URL=$VITE_LIVEKIT_URL
ENV VITE_LIVEKIT_API_KEY=$VITE_LIVEKIT_API_KEY
ENV VITE_LIVEKIT_API_SECRET=$VITE_LIVEKIT_API_SECRET

COPY . .
RUN npm run build

# ── Serve stage ───────────────────────────────────────────────
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
