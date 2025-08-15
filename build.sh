#!/bin/bash

# Install dependencies
export PYTHONPATH=/app
pip install --upgrade pip && \
pip install --timeout 1000 --retries 5 \
  --index-url https://pypi.org/simple/ \
  --extra-index-url https://pypi.python.org/simple/ \
  --trusted-host pypi.org --trusted-host pypi.python.org \
  -r requirements.txt