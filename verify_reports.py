#!/usr/bin/env python3
"""Verify report calculations are correct"""

from app import db, Task, app
from datetime import date, datetime

with app.app_context():
    all_tasks = Task.query.all()
    today = date.today()
    
    total = len(all_tasks)
    completed = sum(1 for t in all_tasks if t.completed)
    pending = total - completed
    
    overdue = 0
    for task in all_tasks:
        if not task.completed:
            if task.recurrence_type == 'once':
                if task.due_date < today:
                    overdue += 1
            elif task.recurrence_type == 'daily':
                if task.due_date < today and (task.recurrence_end_date is None or task.recurrence_end_date >= today):
                    overdue += 1
            elif task.recurrence_type == 'selective':
                selective_dates = task.get_selective_dates()
                for d_str in selective_dates:
                    d = datetime.strptime(d_str, '%Y-%m-%d').date()
                    if d < today:
                        overdue += 1
                        break
    
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    print(f'Today: {today}')
    print(f'Total Tasks: {total}')
    print(f'Completed: {completed}')
    print(f'Pending: {pending}')
    print(f'Overdue: {overdue}')
    print(f'Completion Rate: {completion_rate:.1f}%')
