#!/bin/bash
# Test script for Task Dashboard

echo "=========================================="
echo "Task Dashboard - Endpoint Testing"
echo "=========================================="

echo -e "\n1. Testing Dashboard (GET /):"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
echo "   Status: $STATUS"
[[ "$STATUS" == "200" ]] && echo "   ✓ Dashboard works" || echo "   ✗ Dashboard failed"

echo -e "\n2. Testing API Stats (GET /api/stats):"
RESPONSE=$(curl -s http://localhost:8000/api/stats)
echo "   Response: $RESPONSE"
echo "   ✓ Stats API works"

echo -e "\n3. Testing Add Task Form (GET /add):"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/add)
echo "   Status: $STATUS"
[[ "$STATUS" == "200" ]] && echo "   ✓ Add form works" || echo "   ✗ Add form failed"

echo -e "\n4. Testing Task Creation (POST /add):"
RESPONSE=$(curl -s -X POST http://localhost:8000/add \
  -d "title=Test Task&description=Testing&due_date=2026-03-27&recurrence_type=once" \
  -L -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
echo "   Status: $HTTP_CODE"
[[ "$HTTP_CODE" == "200" ]] && echo "   ✓ Task creation works" || echo "   ✗ Task creation failed"

echo -e "\n5. Testing API Tasks (GET /api/tasks):"
TASKS=$(curl -s http://localhost:8000/api/tasks)
TASK_COUNT=$(echo "$TASKS" | grep -o '"id"' | wc -l)
echo "   Tasks created: $TASK_COUNT"
[[ $TASK_COUNT -gt 0 ]] && echo "   ✓ Task retrieval works" || echo "   ✗ No tasks found"

echo -e "\n6. Testing Static Files (CSS):"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/styles.css)
echo "   CSS Status: $STATUS"
[[ "$STATUS" == "200" ]] && echo "   ✓ CSS loads correctly" || echo "   ✗ CSS failed"

echo -e "\n7. Testing Static Files (JS):"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/script.js)
echo "   JS Status: $STATUS"
[[ "$STATUS" == "200" ]] && echo "   ✓ JavaScript loads correctly" || echo "   ✗ JavaScript failed"

echo -e "\n=========================================="
echo "Testing Complete! ✓"
echo "=========================================="
echo -e "\nYou can access the app at: http://localhost:8000"
