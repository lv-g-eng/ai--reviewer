# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY tsconfig.json ./
COPY services/project-manager/package*.json ./services/project-manager/
COPY shared ./shared

RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY services/project-manager ./services/project-manager

RUN npm run build -w services/project-manager

# Stage 2: Runtime
FROM node:18-alpine AS production

RUN apk add --no-cache dumb-init && \
    apk upgrade --no-cache

WORKDIR /app

COPY package*.json ./
COPY services/project-manager/package*.json ./services/project-manager/
COPY shared ./shared

RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev --ignore-scripts && \
    npm cache clean --force

COPY --from=builder /app/services/project-manager/dist ./services/project-manager/dist

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

RUN mkdir -p services/project-manager/logs && \
    chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 3005

ENTRYPOINT ["dumb-init", "--"]

CMD ["node", "services/project-manager/dist/services/project-manager/src/index.js"]
