#!/usr/bin/env python3
"""
QR Code Generator for Task Dashboard Android Installation
Creates QR codes for easy app installation on Android devices
"""

import qrcode
import os
from PIL import Image, ImageDraw, ImageFont
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "192.168.0.4"  # fallback

def create_qr_code(url, filename, title="Task Dashboard"):
    """Create a QR code with custom styling"""

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Create a larger image with title
    img_width = max(qr_img.size[0], 300)
    img_height = qr_img.size[1] + 100

    # Create new image with white background
    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)

    # Add title
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Center the title
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (img_width - text_width) // 2
    draw.text((text_x, 10), title, fill="black", font=font)

    # Add URL below title
    try:
        small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
    except:
        small_font = ImageFont.load_default()

    url_bbox = draw.textbbox((0, 0), url, font=small_font)
    url_width = url_bbox[2] - url_bbox[0]
    url_x = (img_width - url_width) // 2
    draw.text((url_x, 40), url, fill="gray", font=small_font)

    # Paste QR code
    qr_x = (img_width - qr_img.size[0]) // 2
    qr_y = 70
    img.paste(qr_img, (qr_x, qr_y))

    # Add instructions at bottom
    instructions = "Scan with Android phone to install"
    inst_bbox = draw.textbbox((0, 0), instructions, font=small_font)
    inst_width = inst_bbox[2] - inst_bbox[0]
    inst_x = (img_width - inst_width) // 2
    draw.text((inst_x, img_height - 25), instructions, fill="black", font=small_font)

    # Save the image
    img.save(filename)
    print(f"✅ QR Code saved as: {filename}")

def main():
    # Get local IP
    local_ip = get_local_ip()
    app_url = f"http://{local_ip}:5001"

    print("📱 Task Dashboard QR Code Generator")
    print("=" * 40)
    print(f"📍 Local IP: {local_ip}")
    print(f"🌐 App URL: {app_url}")
    print()

    # Create QR codes for different purposes
    qr_codes = [
        {
            "url": app_url,
            "filename": "task_dashboard_qr.png",
            "title": "📋 Task Dashboard"
        },
        {
            "url": f"{app_url}/add",
            "filename": "add_task_qr.png",
            "title": "➕ Add New Task"
        },
        {
            "url": f"{app_url}/reports",
            "filename": "reports_qr.png",
            "title": "📊 View Reports"
        }
    ]

    for qr_info in qr_codes:
        create_qr_code(qr_info["url"], qr_info["filename"], qr_info["title"])

    print()
    print("🎉 QR Codes Generated!")
    print()
    print("📋 Installation Instructions:")
    print("1. Transfer the QR code images to your Android device")
    print("2. Open camera app or QR scanner on Android")
    print("3. Scan the QR code to open Task Dashboard")
    print("4. Tap 'Add to Home Screen' for app-like experience")
    print()
    print("🔗 Direct Links:")
    print(f"   Main App: {app_url}")
    print(f"   Add Task: {app_url}/add")
    print(f"   Reports: {app_url}/reports")
    print()
    print("💡 Pro Tip: For best experience, add to home screen as PWA!")

if __name__ == "__main__":
    main()