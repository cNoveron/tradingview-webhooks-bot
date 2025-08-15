FROM python:3.11-alpine
LABEL name="tvwb"
LABEL version="1.0"

COPY src /app
WORKDIR /app
ENV PYTHONPATH=/app

# Create .env file with environment variables available during build
RUN echo "# Environment variables for TVWB" > .env && \
    echo "BITSO_API_KEY=${BITSO_API_KEY}" >> .env && \
    echo "BITSO_API_SECRET=${BITSO_API_SECRET}" >> .env && \
    echo "BITSO_ENVIRONMENT=${BITSO_ENVIRONMENT:-staging}" >> .env && \
    echo "RECALL_API_KEY=${RECALL_API_KEY}" >> .env && \
    echo "RECALL_ENVIRONMENT=${RECALL_ENVIRONMENT:-sandbox}" >> .env && \
    if [ -n "${BITSO_PROD_BASE_URL}" ]; then echo "BITSO_PROD_BASE_URL=${BITSO_PROD_BASE_URL}" >> .env; fi && \
    if [ -n "${BITSO_STAGE_BASE_URL}" ]; then echo "BITSO_STAGE_BASE_URL=${BITSO_STAGE_BASE_URL}" >> .env; fi && \
    if [ -n "${RECALL_PROD_BASE_URL}" ]; then echo "RECALL_PROD_BASE_URL=${RECALL_PROD_BASE_URL}" >> .env; fi && \
    if [ -n "${RECALL_SANDBOX_BASE_URL}" ]; then echo "RECALL_SANDBOX_BASE_URL=${RECALL_SANDBOX_BASE_URL}" >> .env; fi

RUN pip install --upgrade pip && \
    pip install --timeout 1000 --retries 5 \
    --index-url https://pypi.org/simple/ \
    --extra-index-url https://pypi.python.org/simple/ \
    --trusted-host pypi.org --trusted-host pypi.python.org \
    -r requirements.txt
EXPOSE 5001
