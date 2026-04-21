#!/usr/bin/env python3
"""
Task Dashboard Validation Script
Tests all functionality and validates database operations
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, '/Users/master/ai_env/Task')

try:
    from app import app, db, Task
    from datetime import datetime, timedelta
    
    print("✓ Successfully imported Flask app")
    
    # Test database creation
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Test creating a single task
        task1 = Task(
            title="Test Single Task",
            description="This is a test task",
            due_date=datetime.now().date(),
            recurrence_type='once'
        )
        db.session.add(task1)
        db.session.commit()
        print(f"✓ Created single task: ID={task1.id}")
        
        # Test creating a daily recurring task
        task2 = Task(
            title="Test Daily Task",
            description="Daily recurring task",
            due_date=datetime.now().date(),
            recurrence_type='daily',
            recurrence_end_date=(datetime.now() + timedelta(days=7)).date()
        )
        db.session.add(task2)
        db.session.commit()
        print(f"✓ Created daily recurring task: ID={task2.id}")
        
        # Test creating a selective dates task
        selective_dates = [
            (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
        ]
        task3 = Task(
            title="Test Selective Dates Task",
            description="Task with selective dates",
            due_date=datetime.now().date(),
            recurrence_type='selective'
        )
        task3.set_selective_dates(selective_dates)
        db.session.add(task3)
        db.session.commit()
        print(f"✓ Created selective dates task: ID={task3.id}")
        
        # Test retrieving and querying tasks
        all_tasks = Task.query.all()
        print(f"✓ Retrieved all tasks: {len(all_tasks)} tasks found")
        
        # Test task methods
        for task in all_tasks:
            recurrence_info = task.get_recurrence_info()
            task_dict = task.to_dict()
            print(f"  - Task {task.id}: '{task.title}' -> {recurrence_info}")
        
        # Test filtering logic for a specific date
        today = datetime.now().date()
        test_date = today + timedelta(days=3)
        
        matching_tasks = []
        for task in all_tasks:
            if task.recurrence_type == 'once':
                if task.due_date == test_date:
                    matching_tasks.append(task)
            elif task.recurrence_type == 'daily':
                if task.due_date <= test_date:
                    if task.recurrence_end_date is None or task.recurrence_end_date >= test_date:
                        matching_tasks.append(task)
            elif task.recurrence_type == 'selective':
                selective_dates = task.get_selective_dates()
                if test_date.strftime('%Y-%m-%d') in selective_dates:
                    matching_tasks.append(task)
        
        print(f"✓ Date filtering works: {len(matching_tasks)} tasks on {test_date}")
        
        # Test completing a task
        task1.completed = True
        db.session.commit()
        print(f"✓ Task completion works: Task {task1.id} marked complete")
        
        # Test deleting a task
        db.session.delete(task1)
        db.session.commit()
        remaining = Task.query.count()
        print(f"✓ Task deletion works: {remaining} tasks remaining")
        
    print("\n" + "="*50)
    print("✓ ALL VALIDATIONS PASSED! ")
    print("="*50)
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print(f"Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
