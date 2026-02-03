#!/bin/bash

# Test Rate Limiting & IP Detection
# Usage: ./test_rate_limit.sh

SERVER="http://192.168.43.190:8080"
ENDPOINT="/api/auth/health"

echo "=== Testing Rate Limit & IP Detection ==="
echo "Server: $SERVER"
echo "Endpoint: $ENDPOINT"
echo ""

# Test 1: Normal requests
echo "[Test 1] Sending 5 normal requests (should succeed)..."
for i in {1..100}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$SERVER$ENDPOINT")
    echo "  Request $i: HTTP $response"
    sleep 0.2
done

echo ""

# Test 2: Trigger rate limit
echo "[Test 2] Sending 2 more requests (should trigger rate limit)..."
for i in {6..7}; do
    response=$(curl -s -w "HTTP %{http_code}" "$SERVER$ENDPOINT")
    echo "  Request $i: $response"
done

echo ""

# Test 3: Check honeypot page
echo "[Test 3] Direct access to honeypot..."
curl -s "$SERVER/honeypot" | grep -o "Nice Try, Diddy" || echo "Honeypot not accessible"

echo ""
echo "=== Check Logs ==="
echo "Access log (last 3):"
tail -3 nginx/logs/access.log | jq -r '"\(.timestamp) | IP: \(.remote_ip) | Status: \(.status) | Rate Limited: \(.rate_limited)"'

echo ""
echo "DOS attempts log:"
[ -f nginx/logs/dos_attempts.log ] && tail -1 nginx/logs/dos_attempts.log | jq -r '"DOS detected from IP: \(.remote_ip)"' || echo "No DOS attempts yet"
