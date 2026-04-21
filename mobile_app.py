#!/usr/bin/env python3
"""
Mobile wrapper for Task Dashboard using Kivy
This creates a native mobile app that embeds the Flask web application
"""

import os
import sys
import threading
import time
import webbrowser
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window

class TaskDashboardApp(App):
    def build(self):
        # Set window properties for mobile
        Window.size = (400, 700)  # Mobile-like dimensions
        Window.minimum_width = 320
        Window.minimum_height = 480

        # Main layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # Header
        header = Label(text='📋 Task Dashboard', font_size=24, bold=True, size_hint_y=0.2)
        layout.add_widget(header)

        # Status label
        self.status_label = Label(text='Starting server...', font_size=16, size_hint_y=0.3)
        layout.add_widget(self.status_label)

        # Open in browser button
        self.browser_button = Button(text='Open in Browser', font_size=18, size_hint_y=0.2, disabled=True)
        self.browser_button.bind(on_press=self.open_in_browser)
        layout.add_widget(self.browser_button)

        # Info label
        info_label = Label(
            text='Server will run on http://127.0.0.1:5001\nUse this on your Android device',
            font_size=14,
            size_hint_y=0.3,
            halign='center'
        )
        layout.add_widget(info_label)

        # Start Flask server in background thread
        self.flask_thread = threading.Thread(target=self.start_flask_server, daemon=True)
        self.flask_thread.start()

        # Check server status periodically
        Clock.schedule_interval(self.check_server_status, 1)

        return layout

    def start_flask_server(self):
        """Start the Flask server as a subprocess"""
        try:
            # Start Flask app as subprocess
            self.server_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            print("Flask server started as subprocess")
        except Exception as e:
            print(f"Flask server error: {e}")
            self.status_label.text = f'Server error: {e}'

    def check_server_status(self, dt):
        """Check if the Flask server is running"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 5001))
            sock.close()
            if result == 0:
                self.status_label.text = '✅ Server is running on port 5001'
                self.browser_button.disabled = False
            else:
                self.status_label.text = '⏳ Starting server...'
        except Exception as e:
            self.status_label.text = f'❌ Connection check failed: {e}'

    def open_in_browser(self, instance):
        """Open the Flask app in the default web browser"""
        webbrowser.open('http://127.0.0.1:5001')
        self.status_label.text = '🌐 Opened in browser!'

if __name__ == '__main__':
    TaskDashboardApp().run()