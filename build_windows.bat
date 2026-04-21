@echo off
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
echo Build complete. Find the executable in dist\
pause
