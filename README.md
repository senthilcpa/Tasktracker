# Task Dashboard - Cross-Platform Task Management Tool

A comprehensive task management dashboard with scheduling, priorities, voice input, calendar export, and email integration. Built with Flask and packaged for Windows, macOS, and Android.

## Features

- ✅ Complete CRUD operations for tasks
- ✅ Advanced scheduling (once, daily, selective dates)
- ✅ Priority system (Low, Medium, High, Urgent)
- ✅ Voice-to-text input with intelligent parsing
- ✅ Calendar export (.ics files) with recurrence
- ✅ Email appointment functionality
- ✅ Time and duration tracking
- ✅ Responsive web interface
- ✅ Cross-platform native executables

## Project Structure

```
Task/
├── app.py                 # Main Flask application
├── mobile_app.py          # Kivy mobile app wrapper
├── requirements.txt       # Python dependencies
├── buildozer.spec         # Android build configuration
├── build_windows.bat      # Windows executable builder
├── build_mac.sh          # macOS executable builder
├── build_android.sh      # Android APK builder
├── templates/            # HTML templates
├── static/               # CSS, JS, images
└── README.md             # This file
```

## Building for Different Platforms

### Windows Executable

1. Ensure Python 3.8+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the build script:
   ```bash
   build_windows.bat
   ```
4. Find the executable in `dist/TaskDashboard.exe`

### macOS Executable

1. Ensure Python 3.8+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make build script executable and run:
   ```bash
   chmod +x build_mac.sh
   ./build_mac.sh
   ```
4. Find the executable in `dist/TaskDashboard.app`

### Android APK

1. Install buildozer:
   ```bash
   pip install buildozer
   ```

2. For Android development, you need:
   - Android SDK
   - Android NDK
   - Java JDK

3. Run the Android build:
   ```bash
   ./build_android.sh
   ```

4. Find the APK in `bin/TaskDashboard-1.0.0-debug.apk`

## Running the Application

### Web Version (Development)
```bash
python app.py
```
Open http://localhost:5000 in your browser

### Mobile Version
```bash
python mobile_app.py
```
This launches the Kivy app with embedded web interface

## Dependencies

- Flask 3.0.0 - Web framework
- SQLAlchemy 2.0.23 - Database ORM
- Kivy 2.3.0 - Mobile app framework
- buildozer 1.5.0 - Android build tool
- PyInstaller 5.13.0 - Desktop packaging

## Database

The application uses SQLite database (`tasks.db`) which is automatically created on first run. The database includes automatic schema upgrades for new features.

## Features Overview

### Task Management
- Create, read, update, delete tasks
- Set priorities and categories
- Track time spent and estimated duration

### Scheduling
- One-time tasks
- Daily recurring tasks
- Custom date selection
- Time-based scheduling

### Voice Input
- Speech-to-text conversion
- Intelligent task parsing
- Voice commands for task creation

### Export Features
- Calendar export (.ics) for integration with calendar apps
- Email appointment creation
- Recurring event support

### Mobile Support
- Native Android app using Kivy
- WebView integration for full web app functionality
- Mobile-optimized interface

## Troubleshooting

### Windows Build Issues
- Ensure all dependencies are installed
- Check Python version (3.8+ required)
- Run as administrator if permission errors occur

### macOS Build Issues
- Ensure Xcode command line tools are installed
- Check for proper Python virtual environment
- Verify file permissions

### Android Build Issues
- Install Android SDK and NDK
- Ensure Java JDK is available
- Check buildozer configuration in `buildozer.spec`
- First build may take longer due to dependency downloads

### Common Issues
- **Port already in use**: Change the port in app.py or mobile_app.py
- **Database errors**: Delete tasks.db and restart (data will be lost)
- **Voice input not working**: Check microphone permissions and browser support

## Development

To modify the application:
1. Edit `app.py` for backend changes
2. Modify templates in `templates/` for UI changes
3. Update `static/` files for styling/scripts
4. For mobile changes, edit `mobile_app.py`

## License

This project is open source. Feel free to modify and distribute.

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python app.py
```

5. **Open your browser:**
Navigate to `http://localhost:5000`

## Project Structure

```
Task/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── tasks.db             # SQLite database (auto-created)
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Dashboard page
│   ├── add_task.html   # Add task form
│   └── edit_task.html  # Edit task form
└── static/             # Static files
    ├── styles.css      # CSS styling
    └── script.js       # JavaScript functionality
```

## Usage Guide

### Adding a Task
1. Click the **"+ Add Task"** button in the navigation bar
2. Enter the task title (required)
3. Add a description (optional)
4. Choose your scheduling option:
   - **Single Task (One date only):** Task appears on that date only
   - **Daily Recurring Task:** Task repeats every day starting from the date
     - Optionally set an end date (leave blank for indefinite recurrence)
   - **Selective Dates:** Choose specific dates when the task should appear
     - Click on dates in the calendar to select them
5. Click **"Create Task"**

### Editing a Task
1. Find the task on the dashboard
2. Click the **✏️ Edit** button
3. Update the task details or scheduling options
4. Click **"Update Task"**

### Completing a Task
1. Check the checkbox next to the task title
2. The task will be marked as completed
3. Uncheck to mark as pending

### Deleting a Task
1. Click the **🗑️ Delete** button on the task
2. Confirm the deletion
3. For recurring tasks, only the task definition is deleted (not individual instances)

### Filtering by Date
1. Use the date picker on the dashboard
2. Or click on a date in the calendar view
3. Tasks for the selected date will be displayed (including all recurring instances for that date)

## Database

The application uses SQLite for data persistence. The database file (`tasks.db`) is automatically created when you first run the application. It stores:
- Task titles and descriptions
- Due dates
- Completion status
- Creation and update timestamps

## API Endpoints

The application provides the following endpoints:

- `GET /` - Main dashboard page
- `GET /add` - Add task form
- `POST /add` - Create new task
- `GET /edit/<id>` - Edit task form
- `POST /edit/<id>` - Update task
- `POST /delete/<id>` - Delete task
- `POST /complete/<id>` - Toggle task completion
- `GET /api/tasks` - Get tasks (JSON)
- `GET /api/stats` - Get dashboard statistics (JSON)

## Keyboard Shortcuts

- **Ctrl/Cmd + N** - Go to add new task page

## Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Customization

### Colors
Edit the CSS variables in `static/styles.css`:
```css
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --danger-color: #e74c3c;
    /* ... more colors ... */
}
```

### Database
To use a different database, modify the connection string in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
```

## Deployment

To deploy this application:

1. Use a production WSGI server (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

2. Set Flask environment to production:
```bash
export FLASK_ENV=production
```

3. Use a reverse proxy (Nginx/Apache) for routing

## Cross-platform App Builds

### macOS

1. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Run the build script:
```bash
./build_mac.sh
```
3. Find the standalone executable in `dist/`.

### Windows

1. Install dependencies:
```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
2. Run the build script:
```bat
build_windows.bat
```
3. Find the standalone executable in `dist\`.

### Mobile (PWA)

This app now includes a web app manifest and service worker, so it can be installed on mobile devices as a Progressive Web App.

1. Run the app locally:
```bash
python app.py
```
2. Open the app in a mobile browser using your machine's IP address, for example:
```
http://192.168.1.100:8000
```
3. Use the browser install prompt to add the app to your home screen.

## Troubleshooting

**Database errors:**
- Delete `tasks.db` and restart the application
- Ensure the directory is writable

**Port already in use:**
- Change the port: `app.run(debug=True, port=5001)`

**Style not loading:**
- Clear browser cache (Ctrl+Shift+Delete)
- Ensure `static` folder exists

## Future Enhancements

- User authentication and multiple user support
- Recurring task templates
- Task categories and tags
- Priority levels
- Email notifications for upcoming tasks
- Dark mode
- Data export (CSV, PDF)
- Task search and filtering
- Collaborative task sharing
- Mobile app
- Task attachments

## License

This project is open source and available for educational and personal use.

## Support

For issues or suggestions, please refer to the code comments or contact the developer.

---

**Happy Task Management!** 📋✨
