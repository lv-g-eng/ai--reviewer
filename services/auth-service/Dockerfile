# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

WORKDIR /app

# Copy root workspace files for dependency installation
COPY package*.json ./
COPY tsconfig.json ./

# Copy service specific files
COPY services/auth-service/package*.json ./services/auth-service/
COPY services/auth-service/tsconfig.json ./services/auth-service/
COPY shared ./shared

# Use npm ci for consistent and faster dependency installation
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy source code
COPY services/auth-service ./services/auth-service

# Build the auth-service workspace
RUN npm run build -w services/auth-service

# Stage 2: Production runtime environment
FROM node:18-alpine AS production

# Install security updates and dumb-init
RUN apk add --no-cache dumb-init && \
    apk upgrade --no-cache

WORKDIR /app

# Copy only production dependencies if possible, or copy everything needed
COPY package*.json ./
COPY services/auth-service/package*.json ./services/auth-service/
COPY shared ./shared

# Install production dependencies only
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev --ignore-scripts && \
    npm cache clean --force

# Copy built files from builder
COPY --from=builder /app/services/auth-service/dist ./services/auth-service/dist

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

# Create logs directory
RUN mkdir -p services/auth-service/logs && \
    chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 3001

ENTRYPOINT ["dumb-init", "--"]

# Run the dist directly for better performance
CMD ["node", "services/auth-service/dist/services/auth-service/src/index.js"]