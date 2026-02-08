# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

WORKDIR /app

# Copy root workspace files
COPY package*.json ./
COPY tsconfig.json ./

# Copy service specific files
COPY services/agentic-ai/package*.json ./services/agentic-ai/
COPY shared ./shared

# Use npm ci for faster installation
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy source code
COPY services/agentic-ai ./services/agentic-ai

# Build the service
RUN npm run build -w services/agentic-ai

# Stage 2: Runtime
FROM node:18-alpine AS production

RUN apk add --no-cache dumb-init && \
    apk upgrade --no-cache

WORKDIR /app

COPY package*.json ./
COPY services/agentic-ai/package*.json ./services/agentic-ai/
COPY shared ./shared

RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev --ignore-scripts && \
    npm cache clean --force

# Copy built files
COPY --from=builder /app/services/agentic-ai/dist ./services/agentic-ai/dist

# Non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

RUN mkdir -p services/agentic-ai/logs && \
    chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 3004

ENTRYPOINT ["dumb-init", "--"]

CMD ["node", "services/agentic-ai/dist/services/agentic-ai/src/index.js"]
