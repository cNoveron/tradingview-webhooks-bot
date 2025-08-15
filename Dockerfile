FROM python:3.11-alpine AS app
LABEL name="tvwb"
LABEL version="1.0"

COPY src /app
WORKDIR /app
ENV PYTHONPATH=/app

ARG BITSO_API_KEY
ARG BITSO_API_SECRET
ARG BITSO_ENVIRONMENT
ARG BITSO_PROD_BASE_URL
ARG BITSO_STAGE_BASE_URL
ARG RECALL_API_KEY
ARG RECALL_ENVIRONMENT
ARG RECALL_PROD_BASE_URL
ARG RECALL_SANDBOX_BASE_URL

# Create .env file with environment variables available during build
RUN echo "# Environment variables for TVWB" > /app/.env && \
    echo "BITSO_API_KEY=${BITSO_API_KEY}" >> /app/.env && \
    echo "BITSO_API_SECRET=${BITSO_API_SECRET}" >> /app/.env && \
    echo "BITSO_ENVIRONMENT=${BITSO_ENVIRONMENT:-staging}" >> /app/.env && \
    echo "RECALL_API_KEY=${RECALL_API_KEY}" >> /app/.env && \
    echo "RECALL_ENVIRONMENT=${RECALL_ENVIRONMENT:-sandbox}" >> /app/.env && \
    if [ -n "${BITSO_PROD_BASE_URL}" ]; then echo "BITSO_PROD_BASE_URL=${BITSO_PROD_BASE_URL}" >> /app/.env; fi && \
    if [ -n "${BITSO_STAGE_BASE_URL}" ]; then echo "BITSO_STAGE_BASE_URL=${BITSO_STAGE_BASE_URL}" >> /app/.env; fi && \
    if [ -n "${RECALL_PROD_BASE_URL}" ]; then echo "RECALL_PROD_BASE_URL=${RECALL_PROD_BASE_URL}" >> /app/.env; fi && \
    if [ -n "${RECALL_SANDBOX_BASE_URL}" ]; then echo "RECALL_SANDBOX_BASE_URL=${RECALL_SANDBOX_BASE_URL}" >> /app/.env; fi

RUN pip install --upgrade pip && \
    pip install --timeout 1000 --retries 5 \
    --index-url https://pypi.org/simple/ \
    --extra-index-url https://pypi.python.org/simple/ \
    --trusted-host pypi.org --trusted-host pypi.python.org \
    -r requirements.txt

# Final stage with nginx
FROM nginx:alpine

# Install Python 3.11 and supervisor
RUN apk add --no-cache python3 python3-dev py3-pip supervisor gcc musl-dev

# Copy Python app from first stage
COPY --from=app /app /app

# Install Python dependencies
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisord.conf

# Create necessary directories
RUN mkdir -p /var/log/supervisor

# Expose port 80 for nginx
EXPOSE 80

ENV PYTHONPATH=/app
# Start supervisor to run both nginx and the Python app
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
