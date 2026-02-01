# Multi-stage build for production optimization
FROM node:18-alpine AS builder

# Install build dependencies
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./
COPY tsconfig.json ./
COPY services/api-gateway/package*.json ./services/api-gateway/
COPY services/api-gateway/tsconfig.json ./services/api-gateway/
COPY shared ./shared

# Install all dependencies (including devDependencies for build)
RUN npm install

# Copy source code
COPY services/api-gateway ./services/api-gateway

# Build the application
RUN npm run build -w services/api-gateway

# Production stage
FROM node:18-alpine AS production

# Install security updates and dumb-init for proper signal handling
RUN apk add --no-cache dumb-init && \
    apk upgrade --no-cache

WORKDIR /app

# Copy package files for production dependencies only
COPY package*.json ./
COPY services/api-gateway/package*.json ./services/api-gateway/
COPY shared ./shared

# Install only production dependencies
RUN npm install --omit=dev --ignore-scripts && \
    npm cache clean --force

# Copy built application from builder stage
COPY --from=builder /app/services/api-gateway/dist ./services/api-gateway/dist

# Create non-root user with specific UID/GID for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

# Create necessary directories with proper permissions
RUN mkdir -p /app/services/api-gateway/logs && \
    mkdir -p /tmp && \
    chown -R nodejs:nodejs /app && \
    chown -R nodejs:nodejs /tmp && \
    chmod 755 /app/services/api-gateway/logs

# Switch to non-root user
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) }).on('error', () => process.exit(1))"

# Expose port
EXPOSE 3000

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["node", "services/api-gateway/dist/services/api-gateway/src/index.js"]