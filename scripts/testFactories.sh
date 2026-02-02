#!/bin/bash
set -e
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "EDIT .env and set secure keys!"
fi
echo "Starting Docker services..."
docker compose up -d
echo "Waiting for PostgreSQL..."
until docker compose exec -T postgres pg_isready -U k_user > /dev/null 2>&1; do
    sleep 1
done
echo "Waiting for Redis..."
until docker compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL ready"
echo "Redis ready"
# Test PostgreSQL
echo ""
echo "Testing PostgreSQL connection..."
docker compose exec -T postgres psql -U k_user -d k_user_management -c "SELECT version();"
# Test Redis
echo ""
echo "Testing Redis connection..."
docker compose exec -T redis redis-cli ping
echo ""
echo "All factories ready!"
echo ""
echo "Next steps:"
echo "1. Install Python deps: poetry install"
echo "2. Start public server: uvicorn public_server:app --port 8001"
echo "3. Start admin server: uvicorn admin_server:app --port 8002"
echo "4. Start nginx: openresty -p \$(pwd)/nginx -c nginx.conf"
