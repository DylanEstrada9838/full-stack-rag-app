# ── Frontend Dockerfile ─────────────────────────────────────────────────────
# Stage 1: Build the React app
# Stage 2: Serve the built files with Nginx
# ---------------------------------------------------------------------------

# ── Stage 1: Build ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies (copy lock files first for better caching)
COPY package.json package-lock.json ./
RUN npm ci

# Receive VITE_API_URL from docker-compose build args
# When set to "" (empty), the app uses relative URLs that nginx proxies.
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL

# Copy source and build
COPY . .
RUN npm run build


# ── Stage 2: Serve with Nginx ────────────────────────────────────────────────
FROM nginx:alpine

# Remove default nginx config and replace with ours
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React files from Stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
