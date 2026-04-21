#!/bin/bash

# Quick Android Access Script
# Get the access URL for Android phone testing

echo "📱 Android Phone Access URL"
echo "==========================="
echo ""

# Get local IP address
IP=$(ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

if [ -z "$IP" ]; then
    echo "❌ Could not determine IP address"
    echo "   Make sure you're connected to a network"
    exit 1
fi

echo "🌐 Access URL: http://$IP:5001"
echo ""
echo "📋 Instructions:"
echo "   1. On your Android phone, open a web browser"
echo "   2. Navigate to the URL above"
echo "   3. Enjoy your Task Dashboard on mobile!"
echo ""
echo "🔍 Server Status:"
curl -s -o /dev/null -w "   Status: HTTP %{http_code}\n" http://127.0.0.1:5001
echo ""
echo "📊 Quick Stats:"
curl -s http://127.0.0.1:5001/api/stats | jq . 2>/dev/null || curl -s http://127.0.0.1:5001/api/stats