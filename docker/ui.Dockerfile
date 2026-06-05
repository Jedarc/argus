# ── Development (Vite dev server) ────────────────────────────────────────────
FROM node:20-alpine AS development

WORKDIR /app
COPY src/ui/package*.json ./
RUN npm install
COPY src/ui/ ./
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# ── Build ─────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app
COPY src/ui/package*.json ./
RUN npm ci --omit=dev
COPY src/ui/ ./
RUN npm run build

# ── Production (nginx) ────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
