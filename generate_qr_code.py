#!/usr/bin/env python3
"""
QR Code Generator for Task Dashboard Android Installation
Generates QR codes for easy app sharing and installation
"""

import qrcode
import sys
from pathlib import Path

def generate_qr_code(url, filename, size=10, border=2):
    """
    Generate a QR code image
    
    Args:
        url: URL to encode
        filename: Output filename
        size: Size of the QR code
        border: Border thickness
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"✅ QR Code generated: {filename}")
    return img

def main():
    # Get local IP
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Alternative method if above doesn't work
    if local_ip == "127.0.0.1":
        import subprocess
        try:
            result = subprocess.check_output(['ifconfig']).decode()
            for line in result.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    local_ip = line.split()[1]
                    break
        except:
            pass
    
    # URLs to encode
    web_url = f"http://{local_ip}:5001"
    pwa_install_url = web_url
    
    print("🔍 QR Code Generator for Task Dashboard")
    print("=" * 50)
    print(f"\n📱 Local Network URL: {web_url}")
    print(f"🌐 Web Access: {pwa_install_url}")
    
    # Generate QR codes
    print("\n📊 Generating QR Codes...")
    
    # Main QR code for web access
    generate_qr_code(web_url, "qr_task_dashboard.png", size=10, border=2)
    
    # PWA Install QR code
    generate_qr_code(pwa_install_url, "qr_pwa_install.png", size=10, border=2)
    
    print("\n✨ QR Codes generated successfully!")
    print("\n📋 Files created:")
    print("   1. qr_task_dashboard.png - Main app access QR code")
    print("   2. qr_pwa_install.png - PWA installation QR code")
    print("\n📸 Instructions:")
    print("   1. Show the QR code on your computer screen")
    print("   2. Scan with Android phone camera or QR code app")
    print("   3. Opens Task Dashboard in browser")
    print("   4. Choose 'Add to Home Screen' for PWA installation")
    print("\n🚀 Ready for distribution!")

if __name__ == "__main__":
    main()