# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY tsconfig.json ./
COPY services/architecture-analyzer/package*.json ./services/architecture-analyzer/
COPY shared ./shared

RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY services/architecture-analyzer ./services/architecture-analyzer

RUN npm run build -w services/architecture-analyzer

# Stage 2: Runtime
FROM node:18-alpine AS production

RUN apk add --no-cache dumb-init && \
    apk upgrade --no-cache

WORKDIR /app

COPY package*.json ./
COPY services/architecture-analyzer/package*.json ./services/architecture-analyzer/
COPY shared ./shared

RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev --ignore-scripts && \
    npm cache clean --force

COPY --from=builder /app/services/architecture-analyzer/dist ./services/architecture-analyzer/dist

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

RUN mkdir -p services/architecture-analyzer/logs && \
    chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 3003

ENTRYPOINT ["dumb-init", "--"]

CMD ["node", "services/architecture-analyzer/dist/services/architecture-analyzer/src/index.js"]
