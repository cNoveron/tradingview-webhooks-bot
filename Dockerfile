FROM python:3.11-alpine

COPY src /app
WORKDIR /app
ENV PYTHONPATH=/app
RUN pip install --upgrade pip && \
    pip install --timeout 1000 --retries 5 \
    --index-url https://pypi.org/simple/ \
    --extra-index-url https://pypi.python.org/simple/ \
    --trusted-host pypi.org --trusted-host pypi.python.org \
    -r requirements.txt
EXPOSE 5001
