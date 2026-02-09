# Frontend Dockerfile - Node.js build and Nginx serve
FROM node:20-alpine as builder

WORKDIR /build

# Copy package files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend .

# Build the application
RUN npm run build

# Nginx runtime stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /build/dist /usr/share/nginx/html

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/index.html || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
