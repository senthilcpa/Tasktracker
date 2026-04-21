#!/bin/bash

# Serve Android Installation Guide
# Opens the installation guide in the default browser

echo "📱 Opening Android Installation Guide..."
echo "========================================"
echo ""

# Check if the HTML file exists
if [ ! -f "android_install.html" ]; then
    echo "❌ Installation guide not found!"
    exit 1
fi

# Get the local IP
IP=$(ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

if [ -z "$IP" ]; then
    IP="192.168.0.4"  # fallback
fi

# Open in browser
if command -v open &> /dev/null; then
    open "file://$(pwd)/android_install.html"
elif command -v xdg-open &> /dev/null; then
    xdg-open "file://$(pwd)/android_install.html"
else
    echo "🌐 Installation Guide: file://$(pwd)/android_install.html"
fi

echo "✅ Installation guide opened!"
echo ""
echo "📋 For Android phone access:"
echo "   Web App: http://$IP:5001"
echo "   Installation Guide: Transfer android_install.html to your phone"
echo ""
echo "📱 QR Codes generated:"
echo "   - task_dashboard_qr.png (main app)"
echo "   - add_task_qr.png (quick add)"
echo "   - reports_qr.png (analytics)"
echo ""
echo "🎯 Transfer these files to your Android device and scan the QR codes!"