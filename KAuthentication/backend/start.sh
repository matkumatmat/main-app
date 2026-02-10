#!/bin/bash

# Set working directory
cd "$(dirname "$0")"

# Set PYTHONPATH to include project root and backend directory
export PYTHONPATH="/home/k/pythonic/py3_14/k-services:/home/k/pythonic/py3_14/k-services/KAuthentication/backend:$PYTHONPATH"

# Load .env from project root
export $(grep -v '^#' ../../.env | xargs)

# Start uvicorn
poetry run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
