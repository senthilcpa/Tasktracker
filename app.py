from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime, timedelta, date
import os
import json
import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import uuid

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "tasks.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='normal')  # 'low', 'normal', 'should_do', 'very_important'
    
    # Time fields (HH:MM format)
    start_time = db.Column(db.String(5), nullable=True)  # HH:MM format
    end_time = db.Column(db.String(5), nullable=True)    # HH:MM format
    
    # Meeting fields
    meeting_email = db.Column(db.String(120), nullable=True)
    guest_emails = db.Column(db.Text, default='')
    google_meet_link = db.Column(db.String(255), nullable=True)
    legacy_comments = db.Column('comments', db.Text, default='')
    comments = db.relationship(
        'TaskComment',
        backref='task',
        cascade='all, delete-orphan',
        order_by='TaskComment.created_at'
    )

    # Scheduling fields
    recurrence_type = db.Column(db.String(20), default='once')  # 'once', 'daily', 'selective'
    recurrence_end_date = db.Column(db.Date, nullable=True)  # For daily recurrence
    selective_dates = db.Column(db.Text, default='')  # JSON string of dates for selective
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_selective_dates(self):
        """Parse selective dates from JSON and normalize nested JSON list strings."""
        if not self.selective_dates:
            return []

        try:
            dates = json.loads(self.selective_dates)
        except json.JSONDecodeError:
            return []

        normalized_dates = []
        if isinstance(dates, list):
            for item in dates:
                if isinstance(item, str) and item.startswith('['):
                    try:
                        nested = json.loads(item)
                        if isinstance(nested, list):
                            normalized_dates.extend([d for d in nested if isinstance(d, str)])
                        else:
                            normalized_dates.append(item)
                    except json.JSONDecodeError:
                        normalized_dates.append(item)
                elif isinstance(item, str):
                    normalized_dates.append(item)
        return normalized_dates
    
    def get_guest_emails(self):
        if not self.guest_emails:
            return []
        try:
            data = json.loads(self.guest_emails)
            if isinstance(data, list):
                return [email.strip() for email in data if isinstance(email, str) and email.strip()]
        except json.JSONDecodeError:
            return [email.strip() for email in self.guest_emails.split(',') if email.strip()]
        return []

    def set_guest_emails(self, emails):
        if not emails:
            self.guest_emails = ''
            return
        if isinstance(emails, str):
            parsed = [email.strip() for email in emails.replace(';', ',').split(',') if email.strip()]
        elif isinstance(emails, list):
            parsed = [email.strip() for email in emails if isinstance(email, str) and email.strip()]
        else:
            parsed = []
        self.guest_emails = json.dumps(parsed)

    def get_comments(self):
        return [comment.text for comment in self.comments]

    def set_selective_dates(self, dates):
        """Set selective dates as JSON"""
        self.selective_dates = json.dumps(dates) if dates else ''
    
    def get_recurrence_info(self):
        """Get human-readable recurrence info"""
        if self.recurrence_type == 'once':
            return 'Single task'
        elif self.recurrence_type == 'daily':
            end = self.recurrence_end_date.strftime('%Y-%m-%d') if self.recurrence_end_date else 'No end date'
            return f'Daily until {end}'
        elif self.recurrence_type == 'selective':
            dates = self.get_selective_dates()
            return f'On {len(dates)} selected dates'
        return ''

    def get_priority_display(self):
        """Get human-readable priority name"""
        priority_map = {
            'low': 'Low Priority',
            'normal': 'Normal',
            'should_do': 'Should Do',
            'very_important': 'Very Important'
        }
        return priority_map.get(self.priority, 'Normal')

    def get_duration_minutes(self):
        """Calculate duration in minutes from start_time and end_time"""
        if not self.start_time or not self.end_time:
            return None
        
        try:
            start_parts = self.start_time.split(':')
            end_parts = self.end_time.split(':')
            
            start_hours = int(start_parts[0])
            start_mins = int(start_parts[1]) if len(start_parts) > 1 else 0
            
            end_hours = int(end_parts[0])
            end_mins = int(end_parts[1]) if len(end_parts) > 1 else 0
            
            start_total_mins = start_hours * 60 + start_mins
            end_total_mins = end_hours * 60 + end_mins
            
            # Handle next day case (e.g., end_time before start_time)
            if end_total_mins < start_total_mins:
                end_total_mins += 24 * 60
            
            return end_total_mins - start_total_mins
        except (ValueError, IndexError):
            return None
    
    def get_duration_display(self):
        """Get human-readable duration string"""
        duration_mins = self.get_duration_minutes()
        if duration_mins is None:
            return None
        
        hours = duration_mins // 60
        mins = duration_mins % 60
        
        if hours > 0 and mins > 0:
            return f"{hours}h {mins}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{mins}m"
    
    def get_time_display(self):
        """Get human-readable time display"""
        if not self.start_time and not self.end_time:
            return None
        elif self.start_time and self.end_time:
            return f"{self.start_time} - {self.end_time}"
        elif self.start_time:
            return f"From {self.start_time}"
        else:
            return f"Until {self.end_time}"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.strftime('%Y-%m-%d'),
            'completed': self.completed,
            'priority': self.priority,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_minutes': self.get_duration_minutes(),
            'duration_display': self.get_duration_display(),
            'time_display': self.get_time_display(),
            'recurrence_type': self.recurrence_type,
            'recurrence_end_date': self.recurrence_end_date.strftime('%Y-%m-%d') if self.recurrence_end_date else None,
            'selective_dates': self.get_selective_dates(),
            'recurrence_info': self.get_recurrence_info(),
            'meeting_email': self.meeting_email,
            'guest_emails': self.get_guest_emails(),
            'google_meet_link': self.google_meet_link,
            'comments': self.get_comments(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class TaskComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables and apply simple schema upgrades
with app.app_context():
    db.create_all()
    
    # Add new time fields if the table already exists without them
    with db.engine.begin() as conn:
        existing_columns = [row[1] for row in conn.execute(text('PRAGMA table_info(task);')).fetchall()]
        if 'start_time' not in existing_columns:
            conn.execute(text('ALTER TABLE task ADD COLUMN start_time VARCHAR(5)'))
        if 'end_time' not in existing_columns:
            conn.execute(text('ALTER TABLE task ADD COLUMN end_time VARCHAR(5)'))
        if 'meeting_email' not in existing_columns:
            conn.execute(text('ALTER TABLE task ADD COLUMN meeting_email VARCHAR(120)'))
        if 'guest_emails' not in existing_columns:
            conn.execute(text('ALTER TABLE task ADD COLUMN guest_emails TEXT'))
        if 'google_meet_link' not in existing_columns:
            conn.execute(text('ALTER TABLE task ADD COLUMN google_meet_link VARCHAR(255)'))
        if 'comments' not in existing_columns:
            conn.execute(text('ALTER TABLE task ADD COLUMN comments TEXT'))

# Routes
@app.route('/')
def index():
    """Display dashboard with date filter"""
    filter_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        filter_datetime = datetime.strptime(filter_date, '%Y-%m-%d').date()
    except ValueError:
        filter_datetime = datetime.now().date()
    
    # Get all tasks
    all_tasks = Task.query.all()
    
    # Filter tasks for the selected date
    tasks = []
    for task in all_tasks:
        if task.recurrence_type == 'once':
            # Show if due date matches
            if task.due_date == filter_datetime:
                tasks.append(task)
        elif task.recurrence_type == 'daily':
            # Show if within date range
            if task.due_date <= filter_datetime:
                if task.recurrence_end_date is None or task.recurrence_end_date >= filter_datetime:
                    tasks.append(task)
        elif task.recurrence_type == 'selective':
            # Show if in selective dates list
            selective_dates = task.get_selective_dates()
            if filter_date in selective_dates:
                tasks.append(task)
    
    # Calculate counts
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.completed)
    
    # Count tasks by priority for this date
    priority_counts = {'very_important': 0, 'should_do': 0, 'normal': 0, 'low': 0}
    for task in tasks:
        if task.priority in priority_counts:
            priority_counts[task.priority] += 1
    
    # Get all dates with tasks for the calendar
    all_dates = set()
    for task in all_tasks:
        if task.recurrence_type == 'once':
            all_dates.add(task.due_date.strftime('%Y-%m-%d'))
        elif task.recurrence_type == 'daily':
            current = task.due_date
            end = task.recurrence_end_date or (datetime.now() + timedelta(days=365)).date()
            while current <= end:
                all_dates.add(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
        elif task.recurrence_type == 'selective':
            for d in task.get_selective_dates():
                all_dates.add(d)
    
    return render_template('index.html', 
                         tasks=tasks,
                         filter_date=filter_date,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         priority_counts=priority_counts,
                         dates_with_tasks=sorted(list(all_dates)))

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """API endpoint to get tasks"""
    filter_date = request.args.get('date')
    
    if filter_date:
        try:
            filter_datetime = datetime.strptime(filter_date, '%Y-%m-%d').date()
            tasks = Task.query.filter(Task.due_date == filter_datetime).all()
        except ValueError:
            tasks = Task.query.all()
    else:
        tasks = Task.query.all()
    
    return jsonify([task.to_dict() for task in tasks])

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    """Add a new task"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        due_date_str = request.form.get('due_date')
        recurrence_type = request.form.get('recurrence_type', 'once')
        
        if not title or not due_date_str:
            return redirect(url_for('add_task'))
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return redirect(url_for('add_task'))
        
        # Get time fields
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        
        meeting_email = request.form.get('meeting_email', '').strip() or None
        guest_emails = request.form.get('guest_emails', '').strip() or None
        google_meet_link = request.form.get('google_meet_link', '').strip() or None
        if google_meet_link and not google_meet_link.startswith('http'):
            google_meet_link = 'https://' + google_meet_link
        if not google_meet_link:
            google_meet_link = generate_google_meet_link()

        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            recurrence_type=recurrence_type,
            priority=request.form.get('priority', 'normal'),
            start_time=start_time if start_time else None,
            end_time=end_time if end_time else None,
            meeting_email=meeting_email,
            google_meet_link=google_meet_link
        )
        task.set_guest_emails(guest_emails)
        
        # Handle different recurrence types
        if recurrence_type == 'daily':
            recurrence_end_str = request.form.get('recurrence_end_date')
            if recurrence_end_str:
                try:
                    task.recurrence_end_date = datetime.strptime(recurrence_end_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
        
        elif recurrence_type == 'selective':
            selective_dates = request.form.getlist('selective_dates')
            if len(selective_dates) == 1 and isinstance(selective_dates[0], str) and selective_dates[0].strip().startswith('['):
                try:
                    parsed_dates = json.loads(selective_dates[0])
                    if isinstance(parsed_dates, list):
                        selective_dates = parsed_dates
                except json.JSONDecodeError:
                    pass
            if selective_dates:
                task.set_selective_dates(selective_dates)
        
        db.session.add(task)
        db.session.commit()
        
        return redirect(url_for('index', date=due_date_str))
    
    # Default to today's date
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_task.html', today=today)

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Edit an existing task"""
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description', '')
        due_date_str = request.form.get('due_date')
        recurrence_type = request.form.get('recurrence_type', 'once')
        
        if not task.title or not due_date_str:
            return redirect(url_for('edit_task', task_id=task_id))
        
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return redirect(url_for('edit_task', task_id=task_id))
        
        task.recurrence_type = recurrence_type
        task.priority = request.form.get('priority', 'normal')
        task.meeting_email = request.form.get('meeting_email', '').strip() or None
        guest_emails = request.form.get('guest_emails', '').strip() or None
        task.set_guest_emails(guest_emails)
        google_meet_link = request.form.get('google_meet_link', '').strip() or None
        if google_meet_link and not google_meet_link.startswith('http'):
            google_meet_link = 'https://' + google_meet_link
        if not google_meet_link:
            google_meet_link = task.google_meet_link or generate_google_meet_link()
        task.google_meet_link = google_meet_link
        
        status = request.form.get('status')
        if status == 'completed':
            task.completed = True
        elif status == 'pending':
            task.completed = False
        
        # Get time fields
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        task.start_time = start_time if start_time else None
        task.end_time = end_time if end_time else None
        
        # Handle different recurrence types
        if recurrence_type == 'daily':
            recurrence_end_str = request.form.get('recurrence_end_date')
            if recurrence_end_str:
                try:
                    task.recurrence_end_date = datetime.strptime(recurrence_end_str, '%Y-%m-%d').date()
                except ValueError:
                    task.recurrence_end_date = None
            else:
                task.recurrence_end_date = None
        
        elif recurrence_type == 'selective':
            selective_dates = request.form.getlist('selective_dates')
            if len(selective_dates) == 1 and isinstance(selective_dates[0], str) and selective_dates[0].strip().startswith('['):
                try:
                    parsed_dates = json.loads(selective_dates[0])
                    if isinstance(parsed_dates, list):
                        selective_dates = parsed_dates
                except json.JSONDecodeError:
                    pass
            if selective_dates:
                task.set_selective_dates(selective_dates)
            else:
                task.set_selective_dates([])
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return redirect(url_for('index', date=due_date_str))
    
    return render_template('edit_task.html', task=task)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    due_date = task.due_date.strftime('%Y-%m-%d')
    db.session.delete(task)
    db.session.commit()
    
    return redirect(url_for('index', date=due_date))

@app.route('/complete/<int:task_id>', methods=['POST'])
def toggle_complete(task_id):
    """Toggle task completion status"""
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'completed': task.completed})

@app.route('/status/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    """Update task completion status explicitly"""
    task = Task.query.get_or_404(task_id)
    payload = request.get_json(silent=True) or {}
    status = payload.get('status') or request.form.get('status')

    if status == 'completed':
        task.completed = True
    elif status == 'pending':
        task.completed = False
    else:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400

    task.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'completed': task.completed})

@app.route('/comment/<int:task_id>', methods=['POST'])
def add_task_comment(task_id):
    task = Task.query.get_or_404(task_id)
    payload = request.get_json(silent=True) or {}
    comment_text = payload.get('comment') or request.form.get('comment')
    if not comment_text or not comment_text.strip():
        return jsonify({'success': False, 'error': 'Comment cannot be empty'}), 400

    comment = TaskComment(task_id=task.id, text=comment_text.strip())
    db.session.add(comment)
    task.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'comments': task.get_comments()})

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    all_tasks = Task.query.all()
    total = len(all_tasks)
    completed = sum(1 for task in all_tasks if task.completed)
    pending = total - completed
    
    return jsonify({
        'total': total,
        'completed': completed,
        'pending': pending
    })

@app.route('/reports')
def reports():
    """Display task status reports"""
    all_tasks = Task.query.all()
    today = date.today()
    
    # Basic stats
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for task in all_tasks if task.completed)
    pending_tasks = total_tasks - completed_tasks
    
    # Overdue tasks (pending tasks with due_date < today)
    overdue_tasks = []
    for task in all_tasks:
        if not task.completed:
            if task.recurrence_type == 'once':
                if task.due_date < today:
                    overdue_tasks.append(task)
            elif task.recurrence_type == 'daily':
                # For daily, only overdue if start date is in the past (before today)
                if task.due_date < today and (task.recurrence_end_date is None or task.recurrence_end_date >= today):
                    overdue_tasks.append(task)
            elif task.recurrence_type == 'selective':
                # For selective, check if any selected date is past and not completed
                selective_dates = task.get_selective_dates()
                for d_str in selective_dates:
                    d = datetime.strptime(d_str, '%Y-%m-%d').date()
                    if d < today:
                        overdue_tasks.append(task)
                        break
    
    # Tasks by recurrence type
    recurrence_stats = {}
    for task in all_tasks:
        rec_type = task.recurrence_type
        if rec_type not in recurrence_stats:
            recurrence_stats[rec_type] = {'total': 0, 'completed': 0}
        recurrence_stats[rec_type]['total'] += 1
        if task.completed:
            recurrence_stats[rec_type]['completed'] += 1
    
    # Tasks by priority with detailed breakdown
    priority_stats = {}
    priority_overdue = {}
    priority_completion_rates = {}
    
    for task in all_tasks:
        pri = task.priority
        if pri not in priority_stats:
            priority_stats[pri] = {'total': 0, 'completed': 0, 'pending': 0, 'overdue': 0}
            priority_overdue[pri] = []
        
        priority_stats[pri]['total'] += 1
        
        if task.completed:
            priority_stats[pri]['completed'] += 1
        else:
            priority_stats[pri]['pending'] += 1
            
            # Check if overdue
            is_overdue = False
            if task.recurrence_type == 'once':
                if task.due_date < today:
                    is_overdue = True
            elif task.recurrence_type == 'daily':
                if task.due_date < today and (task.recurrence_end_date is None or task.recurrence_end_date >= today):
                    is_overdue = True
            elif task.recurrence_type == 'selective':
                selective_dates = task.get_selective_dates()
                for d_str in selective_dates:
                    d = datetime.strptime(d_str, '%Y-%m-%d').date()
                    if d < today:
                        is_overdue = True
                        break
            
            if is_overdue:
                priority_stats[pri]['overdue'] += 1
                priority_overdue[pri].append(task)
    
    # Calculate completion rates by priority
    for pri, stats in priority_stats.items():
        if stats['total'] > 0:
            priority_completion_rates[pri] = round((stats['completed'] / stats['total']) * 100, 1)
        else:
            priority_completion_rates[pri] = 0
    
    # Sort priorities by importance for display
    priority_order = {'very_important': 0, 'should_do': 1, 'normal': 2, 'low': 3}
    sorted_priorities = sorted(priority_stats.keys(), key=lambda x: priority_order.get(x, 4))
    
    # Get recent tasks by priority (last 5 created per priority)
    recent_tasks_by_priority = {}
    for pri in sorted_priorities:
        priority_tasks = [t for t in all_tasks if t.priority == pri]
        recent_tasks_by_priority[pri] = sorted(priority_tasks, key=lambda x: x.created_at, reverse=True)[:5]
    
    # Completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return render_template('reports.html',
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         pending_tasks=pending_tasks,
                         overdue_tasks=len(overdue_tasks),
                         recurrence_stats=recurrence_stats,
                         priority_stats=priority_stats,
                         priority_overdue=priority_overdue,
                         priority_completion_rates=priority_completion_rates,
                         sorted_priorities=sorted_priorities,
                         recent_tasks_by_priority=recent_tasks_by_priority,
                         completion_rate=round(completion_rate, 1),
                         today=today)

@app.route('/reports/tasks/<filter_type>')
def report_tasks(filter_type):
    """Display filtered tasks from reports"""
    all_tasks = Task.query.all()
    today = date.today()
    filtered_tasks = []
    title = ''
    
    if filter_type == 'all':
        filtered_tasks = all_tasks
        title = 'All Tasks'
    elif filter_type == 'completed':
        filtered_tasks = [t for t in all_tasks if t.completed]
        title = 'Completed Tasks'
    elif filter_type == 'pending':
        filtered_tasks = [t for t in all_tasks if not t.completed]
        title = 'Pending Tasks'
    elif filter_type == 'overdue':
        # Get overdue tasks using same logic as reports
        for task in all_tasks:
            if not task.completed:
                if task.recurrence_type == 'once':
                    if task.due_date < today:
                        filtered_tasks.append(task)
                elif task.recurrence_type == 'daily':
                    if task.due_date < today and (task.recurrence_end_date is None or task.recurrence_end_date >= today):
                        filtered_tasks.append(task)
                elif task.recurrence_type == 'selective':
                    selective_dates = task.get_selective_dates()
                    for d_str in selective_dates:
                        d = datetime.strptime(d_str, '%Y-%m-%d').date()
                        if d < today:
                            filtered_tasks.append(task)
                            break
        title = 'Overdue Tasks'
    
    # Sort by priority (very_important > should_do > normal > low) and due date
    priority_order = {'very_important': 0, 'should_do': 1, 'normal': 2, 'low': 3}
    filtered_tasks.sort(key=lambda t: (priority_order.get(t.priority, 2), t.due_date))
    
    return render_template('report_tasks.html',
                         tasks=filtered_tasks,
                         filter_type=filter_type,
                         title=title,
                         total=len(filtered_tasks))

@app.route('/search')
def search():
    """Search tasks"""
    query = request.args.get('q', '').lower()
    priority = request.args.get('priority', '')
    status = request.args.get('status', '')
    
    all_tasks = Task.query.all()
    results = []
    
    for task in all_tasks:
        # Filter by search query
        if query and query not in task.title.lower() and query not in task.description.lower():
            continue
        
        # Filter by priority
        if priority and task.priority != priority:
            continue
        
        # Filter by status
        if status == 'completed' and not task.completed:
            continue
        elif status == 'pending' and task.completed:
            continue
        
        results.append(task)
    
    # Sort by priority and due date
    priority_order = {'very_important': 0, 'should_do': 1, 'normal': 2, 'low': 3}
    results.sort(key=lambda t: (priority_order.get(t.priority, 2), t.due_date))
    
    return render_template('search_results.html',
                         tasks=results,
                         query=query,
                         priority=priority,
                         status=status,
                         total=len(results))

@app.route('/calendar/<int:task_id>')
def export_task_calendar(task_id):
    """Export a single task as iCal file"""
    task = Task.query.get_or_404(task_id)
    
    # Generate iCal content
    ical_content = generate_ical_content([task])
    
    # Create response
    response = make_response(ical_content)
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="{task.title.replace(" ", "_")}.ics"'
    
    return response

@app.route('/calendar/export')
def export_calendar():
    """Export all tasks as iCal file"""
    filter_date = request.args.get('date')
    priority = request.args.get('priority')
    
    all_tasks = Task.query.all()
    filtered_tasks = []
    
    for task in all_tasks:
        # Filter by date if specified
        if filter_date:
            try:
                filter_datetime = datetime.strptime(filter_date, '%Y-%m-%d').date()
                if task.recurrence_type == 'once':
                    if task.due_date != filter_datetime:
                        continue
                elif task.recurrence_type == 'daily':
                    if not (task.due_date <= filter_datetime and 
                           (task.recurrence_end_date is None or task.recurrence_end_date >= filter_datetime)):
                        continue
                elif task.recurrence_type == 'selective':
                    if filter_date not in task.get_selective_dates():
                        continue
            except ValueError:
                pass
        
        # Filter by priority if specified
        if priority and task.priority != priority:
            continue
            
        filtered_tasks.append(task)
    
    # Generate iCal content
    ical_content = generate_ical_content(filtered_tasks)
    
    # Create response
    response = make_response(ical_content)
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    
    filename = 'tasks'
    if filter_date:
        filename += f'_{filter_date}'
    if priority:
        filename += f'_{priority}'
    filename += '.ics'
    
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def format_ical_datetime(event_date, time_str=None):
    """Return an iCal datetime string for a date and optional time."""
    if time_str:
        clean_time = time_str.replace(':', '')
        return event_date.strftime('%Y%m%d') + 'T' + clean_time + '00'
    return event_date.strftime('%Y%m%d')


def generate_ical_content(tasks, organizer_email=None, attendee_emails=None):
    """Generate iCal content for tasks"""
    if attendee_emails is None:
        attendee_emails = []
    elif isinstance(attendee_emails, str):
        attendee_emails = [attendee_emails]
    elif isinstance(attendee_emails, set):
        attendee_emails = list(attendee_emails)

    ical_lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Task Dashboard//Task Calendar//EN',
        'CALSCALE:GREGORIAN'
    ]

    for task in tasks:
        # Generate unique UID for the event
        event_uid = str(uuid.uuid4())
        
        # Helper for all-day or timed event lines
        def build_event_lines(event_date, summary_suffix=''):
            has_time = bool(task.start_time and task.end_time)
            dtstart_value = format_ical_datetime(event_date, task.start_time if has_time else None)
            if has_time:
                start_dt = datetime.strptime(dtstart_value, '%Y%m%dT%H%M%S')
                end_dt = datetime.strptime(format_ical_datetime(event_date, task.end_time), '%Y%m%dT%H%M%S')
                if end_dt <= start_dt:
                    end_dt += timedelta(days=1)
                dtend_value = end_dt.strftime('%Y%m%dT%H%M%S')
            else:
                dtend_value = (event_date + timedelta(days=1)).strftime('%Y%m%d')

            lines = [
                'BEGIN:VEVENT',
                f'UID:{event_uid}@taskdashboard',
                f'SUMMARY:{task.title}{summary_suffix}',
                f'DESCRIPTION:{task.description}',
                f'PRIORITY:{get_priority_number(task.priority)}',
                f'STATUS:{"COMPLETED" if task.completed else "CONFIRMED"}',
                f'CREATED:{task.created_at.strftime("%Y%m%dT%H%M%SZ")}',
                f'LAST-MODIFIED:{task.updated_at.strftime("%Y%m%dT%H%M%SZ")}'
            ]
            if has_time:
                lines.insert(2, f'DTSTART:{dtstart_value}')
                lines.insert(3, f'DTEND:{dtend_value}')
            else:
                lines.insert(2, f'DTSTART;VALUE=DATE:{dtstart_value}')
                lines.insert(3, f'DTEND;VALUE=DATE:{dtend_value}')

            if task.google_meet_link:
                lines.append(f'URL:{task.google_meet_link}')
                lines.append('LOCATION:Google Meet')

            if organizer_email:
                lines.append(f'ORGANIZER:mailto:{organizer_email}')
            for attendee in attendee_emails:
                if attendee:
                    lines.append(f'ATTENDEE;CN=Participant:mailto:{attendee}')
            return lines

        if task.recurrence_type == 'selective':
            selective_dates = task.get_selective_dates()
            if selective_dates:
                for idx, date_str in enumerate(selective_dates):
                    event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    event_uid = str(uuid.uuid4())
                    event_lines = build_event_lines(event_date, ' (Scheduled)')
                    event_lines.append('END:VEVENT')
                    ical_lines.extend(event_lines)
            else:
                event_date = task.due_date
                event_lines = build_event_lines(event_date)
                event_lines.append('END:VEVENT')
                ical_lines.extend(event_lines)
        else:
            event_date = task.due_date
            event_lines = build_event_lines(event_date)
            if task.recurrence_type == 'daily':
                if task.recurrence_end_date:
                    until_value = task.recurrence_end_date.strftime('%Y%m%d')
                    event_lines.append(f'RRULE:FREQ=DAILY;UNTIL={until_value}')
                else:
                    event_lines.append('RRULE:FREQ=DAILY')
            event_lines.append('END:VEVENT')
            ical_lines.extend(event_lines)

    ical_lines.append('END:VCALENDAR')
    return '\r\n'.join(ical_lines)

def get_priority_number(priority):
    """Convert priority to iCal priority number (1-9, 1=highest)"""
    priority_map = {
        'very_important': 1,
        'should_do': 3,
        'normal': 5,
        'low': 7
    }
    return priority_map.get(priority, 5)


def format_google_calendar_datetime(date_obj, time_str=None):
    if time_str:
        clean_time = time_str.replace(':', '')
        return date_obj.strftime('%Y%m%dT') + clean_time + '00'
    return date_obj.strftime('%Y%m%d')


def generate_google_meet_link():
    alias = uuid.uuid4().hex[:10]
    return f'https://meet.google.com/lookup/{alias}'


def build_google_calendar_link(task):
    if task.recurrence_type == 'selective':
        selective_dates = task.get_selective_dates()
        if selective_dates:
            first_date = datetime.strptime(selective_dates[0], '%Y-%m-%d').date()
        else:
            first_date = task.due_date
    else:
        first_date = task.due_date

    if task.start_time and task.end_time:
        start_value = format_google_calendar_datetime(first_date, task.start_time)
        end_value = format_google_calendar_datetime(first_date, task.end_time)
    else:
        start_value = first_date.strftime('%Y%m%d')
        end_value = (first_date + timedelta(days=1)).strftime('%Y%m%d')

    details = task.description or ''
    if task.google_meet_link:
        if details:
            details += '\n\n'
        details += f'Join meeting: {task.google_meet_link}'

    params = [
        ('action', 'TEMPLATE'),
        ('text', task.title),
        ('details', details),
        ('location', task.google_meet_link or 'Google Meet'),
        ('dates', f'{start_value}/{end_value}')
    ]

    if task.meeting_email:
        params.append(('add', task.meeting_email))
    for guest in task.get_guest_emails():
        if guest and guest != task.meeting_email:
            params.append(('add', guest))

    if task.recurrence_type == 'daily':
        if task.recurrence_end_date:
            params.append(('recur', f'RRULE:FREQ=DAILY;UNTIL={task.recurrence_end_date.strftime("%Y%m%d")}'))
        else:
            params.append(('recur', 'RRULE:FREQ=DAILY'))

    return 'https://calendar.google.com/calendar/render?' + urllib.parse.urlencode(params, doseq=True, quote_via=urllib.parse.quote)


@app.route('/schedule/<int:task_id>')
def schedule_meeting(task_id):
    task = Task.query.get_or_404(task_id)
    if not task.google_meet_link:
        task.google_meet_link = generate_google_meet_link()
        task.updated_at = datetime.utcnow()
        db.session.commit()
    return redirect(build_google_calendar_link(task))


@app.route('/email/<int:task_id>', methods=['GET', 'POST'])
def email_task(task_id):
    """Send task as email appointment"""
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        recipient_email = request.form.get('email')
        sender_email = request.form.get('sender_email', 'taskdashboard@example.com')
        sender_password = request.form.get('sender_password')
        google_meet_link = request.form.get('google_meet_link', '').strip() or task.google_meet_link
        
        if google_meet_link and not google_meet_link.startswith('http'):
            google_meet_link = 'https://' + google_meet_link

        if not google_meet_link:
            google_meet_link = 'https://meet.google.com/new'

        if not recipient_email or not sender_email or not sender_password:
            return render_template('email_task.html', task=task, error='All fields are required')
        
        task.meeting_email = recipient_email
        task.google_meet_link = google_meet_link
        task.updated_at = datetime.utcnow()

        recipients = [recipient_email] + task.get_guest_emails()
        recipients = [email for email in dict.fromkeys(recipients) if email]

        try:
            # Send email with iCal attachment
            success = send_task_email(task, recipients, sender_email, sender_password, google_meet_link=google_meet_link)
            if success:
                db.session.commit()
                return render_template('email_task.html', task=task, success='Email sent successfully!')
            else:
                return render_template('email_task.html', task=task, error='Failed to send email')
        except Exception as e:
            return render_template('email_task.html', task=task, error=f'Error: {str(e)}')
    
    return render_template('email_task.html', task=task)

def send_task_email(task, recipient_emails, sender_email, sender_password, google_meet_link=None):
    """Send task as email with iCal attachment"""
    try:
        if google_meet_link and not google_meet_link.startswith('http'):
            google_meet_link = 'https://' + google_meet_link

        recipients = recipient_emails if isinstance(recipient_emails, list) else [recipient_emails]
        recipients = [email for email in recipients if email]

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Task Appointment: {task.title}"
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipients)
        
        attendee_list = recipients
        primary_participant = recipient_emails[0] if isinstance(recipient_emails, list) and recipient_emails else recipients[0]
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>Task Appointment: {task.title}</h2>
            <p><strong>Description:</strong> {task.description or 'No description'}</p>
            <p><strong>Due Date:</strong> {task.due_date.strftime('%Y-%m-%d')}</p>
            {f'<p><strong>Time:</strong> {task.get_time_display()}</p>' if task.get_time_display() else ''}
            {f'<p><strong>Duration:</strong> {task.get_duration_display()}</p>' if task.get_duration_display() else ''}
            <p><strong>Priority:</strong> {task.get_priority_display()}</p>
            <p><strong>Schedule:</strong> {task.get_recurrence_info()}</p>
            <p><strong>Participants:</strong> {', '.join(attendee_list)}</p>
            {f'<p><strong>Google Meet Link:</strong> <a href="{google_meet_link}" target="_blank">{google_meet_link}</a></p>' if google_meet_link else ''}
            <p><strong>Status:</strong> {'Completed' if task.completed else 'Pending'}</p>
            <p>This task has been attached as a calendar appointment (.ics file) that you can import into your calendar application.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Attach iCal file
        ical_content = generate_ical_content([task], organizer_email=sender_email, attendee_emails=attendee_list)
        
        # Create attachment
        attachment = MIMEBase('text', 'calendar')
        attachment.set_payload(ical_content)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=f'{task.title.replace(" ", "_")}.ics')
        attachment.add_header('Content-Type', 'text/calendar; charset=utf-8; method=REQUEST')
        
        msg.attach(attachment)
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
