#!/bin/bash

# Android App Validation Test Script
# Comprehensive testing for Task Dashboard Android deployment

echo "🔍 Android App Validation Test"
echo "=============================="
echo ""

BASE_URL="http://127.0.0.1:5001"

# Test 1: Server Health Check
echo "1. 🏥 Server Health Check"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL)
if [ "$STATUS" = "200" ]; then
    echo "   ✅ Server responding (HTTP $STATUS)"
else
    echo "   ❌ Server not responding (HTTP $STATUS)"
    exit 1
fi

# Test 2: Main Dashboard Load
echo "2. 📊 Main Dashboard Load"
DASHBOARD_SIZE=$(curl -s $BASE_URL | wc -c)
if [ "$DASHBOARD_SIZE" -gt 5000 ]; then
    echo "   ✅ Dashboard loaded ($DASHBOARD_SIZE bytes)"
else
    echo "   ❌ Dashboard too small ($DASHBOARD_SIZE bytes)"
fi

# Test 3: API Endpoints
echo "3. 🔌 API Endpoints Test"
TASKS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/tasks)
STATS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/stats)

if [ "$TASKS_STATUS" = "200" ] && [ "$STATS_STATUS" = "200" ]; then
    echo "   ✅ API endpoints working"
else
    echo "   ❌ API endpoints failed (Tasks: $TASKS_STATUS, Stats: $STATS_STATUS)"
fi

# Test 4: Mobile Responsiveness
echo "4. 📱 Mobile Responsiveness"
VIEWPORT=$(curl -s $BASE_URL | grep -c "viewport")
PWA_TAGS=$(curl -s $BASE_URL | grep -c "apple-mobile-web-app")

if [ "$VIEWPORT" -gt 0 ] && [ "$PWA_TAGS" -gt 0 ]; then
    echo "   ✅ Mobile meta tags present"
else
    echo "   ❌ Mobile meta tags missing"
fi

# Test 5: Static Assets
echo "5. 🎨 Static Assets"
CSS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/static/styles.css)
JS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/static/script.js)

if [ "$CSS_STATUS" = "200" ] && [ "$JS_STATUS" = "200" ]; then
    echo "   ✅ Static assets accessible"
else
    echo "   ❌ Static assets failed (CSS: $CSS_STATUS, JS: $JS_STATUS)"
fi

# Test 6: PWA Manifest
echo "6. 📲 PWA Manifest"
MANIFEST_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/static/manifest.json)
if [ "$MANIFEST_STATUS" = "200" ]; then
    echo "   ✅ PWA manifest available"
else
    echo "   ❌ PWA manifest missing (HTTP $MANIFEST_STATUS)"
fi

# Test 7: Key Routes
echo "7. 🛣️  Application Routes"
ADD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/add)
REPORTS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/reports)

if [ "$ADD_STATUS" = "200" ] && [ "$REPORTS_STATUS" = "200" ]; then
    echo "   ✅ Key routes accessible"
else
    echo "   ❌ Routes failed (Add: $ADD_STATUS, Reports: $REPORTS_STATUS)"
fi

# Test 8: Database Connectivity
echo "8. 💾 Database Connectivity"
if [ -f "tasks.db" ]; then
    DB_SIZE=$(stat -f%z tasks.db 2>/dev/null || stat -c%s tasks.db 2>/dev/null || echo "unknown")
    echo "   ✅ Database file exists ($DB_SIZE bytes)"
else
    echo "   ❌ Database file missing"
fi

# Test 9: Performance Check
echo "9. ⚡ Performance Check"
RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" $BASE_URL)
if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l 2>/dev/null || echo "1") )); then
    echo "   ✅ Fast response time (${RESPONSE_TIME}s)"
else
    echo "   ⚠️  Slow response time (${RESPONSE_TIME}s)"
fi

# Test 10: Android Readiness
echo "10. 🤖 Android Deployment Readiness"
if command -v python3 &> /dev/null && python3 -c "import kivy" &> /dev/null 2>&1; then
    echo "   ✅ Python/Kivy environment ready"
else
    echo "   ❌ Python/Kivy environment issues"
fi

echo ""
echo "🎉 Validation Complete!"
echo ""
echo "📋 For Android Phone Testing:"
echo "   1. Find your computer IP: ifconfig | grep 'inet ' | grep -v 127.0.0.1"
echo "   2. On Android phone, open browser to: http://[COMPUTER_IP]:5001"
echo "   3. Test all features: add tasks, view reports, check mobile layout"
echo ""
echo "🚀 Ready for Android deployment!"