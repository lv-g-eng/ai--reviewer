# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY tsconfig.json ./
COPY services/code-review-engine/package*.json ./services/code-review-engine/
COPY shared ./shared

RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY services/code-review-engine ./services/code-review-engine

RUN npm run build -w services/code-review-engine

# Stage 2: Runtime
FROM node:18-alpine AS production

RUN apk add --no-cache dumb-init && \
    apk upgrade --no-cache

WORKDIR /app

COPY package*.json ./
COPY services/code-review-engine/package*.json ./services/code-review-engine/
COPY shared ./shared

RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev --ignore-scripts && \
    npm cache clean --force

COPY --from=builder /app/services/code-review-engine/dist ./services/code-review-engine/dist

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

RUN mkdir -p services/code-review-engine/logs && \
    chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 3002

ENTRYPOINT ["dumb-init", "--"]

CMD ["node", "services/code-review-engine/dist/services/code-review-engine/src/index.js"]
