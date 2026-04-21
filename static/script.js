// Task Dashboard - Additional JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N for new task
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const addBtn = document.querySelector('a[href*="add"]');
            if (addBtn) {
                window.location.href = addBtn.href;
            }
        }
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('.task-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const titleInput = this.querySelector('[name="title"]');
            const dueDateInput = this.querySelector('[name="due_date"]');

            if (!titleInput.value.trim()) {
                e.preventDefault();
                showNotification('Please enter a task title', 'error');
                titleInput.focus();
                return;
            }

            if (!dueDateInput.value) {
                e.preventDefault();
                showNotification('Please select a due date', 'error');
                dueDateInput.focus();
                return;
            }
        });
    });

    // Improve touch events
    addTouchFriendlyInteractions();
});

// Touch-friendly interactions
function addTouchFriendlyInteractions() {
    // Make checkboxes larger on mobile
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('touchstart', function() {
            this.blur();
        }, { passive: true });
    });

    // Improve button touch targets
    const buttons = document.querySelectorAll('.btn, .btn-icon');
    buttons.forEach(button => {
        button.addEventListener('touchend', function(e) {
            this.style.opacity = '0.7';
            setTimeout(() => {
                this.style.opacity = '1';
            }, 100);
        });
    });

    // Add haptic feedback on mobile (if available)
    if (navigator.vibrate) {
        const clickables = document.querySelectorAll('button, a.btn, input[type="checkbox"]');
        clickables.forEach(element => {
            element.addEventListener('click', function() {
                navigator.vibrate(10); // Short vibration
            });
        });
    }
}

// Show notification messages
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        left: 20px;
        padding: 15px 20px;
        border-radius: 6px;
        background: ${type === 'error' ? '#e74c3c' : type === 'success' ? '#2ecc71' : '#3498db'};
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideInRight 0.3s ease;
        text-align: center;
        max-width: 100%;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Bind inline task status radios and buttons
    function bindTaskStatusControls() {
        const statusRadios = document.querySelectorAll('.status-radio');
        statusRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const taskId = this.getAttribute('data-task-id');
                const status = this.value;
                setTaskStatus(taskId, status);
            });
        });

        const statusButtons = document.querySelectorAll('.status-action-btn');
        statusButtons.forEach(button => {
            button.addEventListener('click', function() {
                const taskId = this.getAttribute('data-task-id');
                const status = this.getAttribute('data-status');
                setTaskStatus(taskId, status);
            });
        });
    }

    function setTaskStatus(taskId, status) {
        fetch(`/status/${taskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Task status updated', 'success');
                window.location.reload();
            } else {
                showNotification('Unable to update status', 'error');
            }
        })
        .catch(() => {
            showNotification('Network error while updating status', 'error');
        });
    }

    // Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}

// Add animation styles dynamically
if (!document.getElementById('notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }

        /* Prevent double-tap zoom on buttons */
        button, a.btn, input[type="checkbox"] {
            touch-action: manipulation;
        }
    `;
    document.head.appendChild(style);
}

// Export functions for use in other scripts
window.TaskDashboardUtils = {
    formatDate,
    showNotification
};

// Voice-to-Text Functionality
class VoiceInputManager {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.currentTarget = null;
        this.awaitingFollowup = false;
        this.followupCallback = null;
        this.init();
    }

    init() {
        // Check if browser supports speech recognition
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported in this browser');
            this.hideVoiceButtons();
            return;
        }

        // Initialize speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        // Configure recognition settings
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        // Set up event handlers
        this.recognition.onstart = () => this.onRecognitionStart();
        this.recognition.onresult = (event) => this.onRecognitionResult(event);
        this.recognition.onend = () => this.onRecognitionEnd();
        this.recognition.onerror = (event) => this.onRecognitionError(event);

        // Set up voice buttons
        this.setupVoiceButtons();
    }

    setupVoiceButtons() {
        const voiceButtons = document.querySelectorAll('.voice-btn');

        voiceButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleVoiceInput(button);
            });

            // Add keyboard support
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleVoiceInput(button);
                }
            });
        });
    }

    toggleVoiceInput(button) {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening(button);
        }
    }

    startListening(button) {
        if (this.isListening) return;

        this.currentTarget = button.dataset.target;
        const targetElement = document.getElementById(this.currentTarget);

        if (!targetElement) {
            showNotification('Target input element not found', 'error');
            return;
        }

        try {
            this.recognition.start();
            button.classList.add('listening');
            button.textContent = '🎙️';
            button.title = 'Listening... Click to stop';

            // Show visual feedback
            showNotification('🎤 Listening... Speak now or click to stop', 'info');
        } catch (error) {
            console.error('Error starting speech recognition:', error);
            showNotification('Error starting voice input. Please try again.', 'error');
        }
    }

    stopListening() {
        if (!this.isListening) return;

        this.recognition.stop();
    }

    onRecognitionStart() {
        this.isListening = true;
        console.log('Voice recognition started');
    }

    onRecognitionResult(event) {
        const results = event.results;
        const transcript = results[0][0].transcript.trim();

        if (transcript) {
            console.log('Raw transcript:', transcript);
            
            // Parse task description for fields
            const parsedTask = this.parseTaskDescription(transcript);
            
            if (this.currentTarget === 'comprehensive-input') {
                if (parsedTask.hasMultipleFields || parsedTask.title) {
                    this.fillMultipleFields(parsedTask);
                    this.askForMissingFields(parsedTask);
                    const comprehensiveField = document.getElementById('comprehensive-input');
                    if (comprehensiveField) {
                        comprehensiveField.value = '';
                    }
                } else {
                    this.insertText(transcript);
                    showNotification(`✅ Heard: "${transcript}" - Try including priority and schedule info`, 'info');
                    this.askForMissingFields(parsedTask);
                }
            } else if (this.currentTarget) {
                // If using a specific field button, insert into that field or parse a full task
                if (parsedTask.hasMultipleFields) {
                    this.fillMultipleFields(parsedTask);
                    this.askForMissingFields(parsedTask);
                } else {
                    this.insertText(transcript);
                    showNotification(`✅ Heard: "${transcript}"`, 'success');
                }
            } else {
                // Follow-up response for voice questions
                if (this.followupCallback) {
                    this.awaitingFollowup = false;
                    const callback = this.followupCallback;
                    this.followupCallback = null;
                    callback(transcript);
                }
            }
        } else {
            showNotification('No speech detected. Please try again.', 'warning');
        }
    }

    parseTaskDescription(transcript) {
        const text = transcript.toLowerCase();
        const result = {
            title: null,
            description: null,
            priority: null,
            recurrenceType: null,
            dueDate: null,
            startTime: null,
            endTime: null,
            hasMultipleFields: false
        };

        // Priority detection patterns
        const priorityPatterns = {
            'very important': 'very_important',
            'very high priority': 'very_important',
            'high priority': 'very_important',
            'should do': 'should_do',
            'important': 'should_do',
            'medium priority': 'normal',
            'normal priority': 'normal',
            'normal': 'normal',
            'low priority': 'low',
            'low': 'low'
        };

        // Schedule detection patterns
        const schedulePatterns = {
            'daily': 'daily',
            'every day': 'daily',
            'once': 'once',
            'one time': 'once',
            'single': 'once',
            'selective': 'selective',
            'custom dates': 'selective',
            'specific dates': 'selective',
            'multiple dates': 'selective'
        };

        // Extract priority
        for (const [pattern, priority] of Object.entries(priorityPatterns)) {
            if (text.includes(pattern)) {
                result.priority = priority;
                result.hasMultipleFields = true;
                break;
            }
        }

        // Extract schedule type
        for (const [pattern, schedule] of Object.entries(schedulePatterns)) {
            if (text.includes(pattern)) {
                result.recurrenceType = schedule;
                result.hasMultipleFields = true;
                break;
            }
        }

        let cleanedText = transcript;

        // Extract time range and start/end times
        const timeRangeMatch = text.match(/from\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*(?:to|until|-)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)/i);
        if (timeRangeMatch) {
            result.startTime = this.parseTimeValue(timeRangeMatch[1]);
            result.endTime = this.parseTimeValue(timeRangeMatch[2]);
            result.hasMultipleFields = true;
            cleanedText = cleanedText.replace(new RegExp(timeRangeMatch[0], 'gi'), '');
        }

        const singleTimeMatch = text.match(/(?:at|by|around|from|in the)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)/i);
        if (singleTimeMatch && !result.startTime) {
            result.startTime = this.parseTimeValue(singleTimeMatch[1]);
            if (result.startTime) {
                result.hasMultipleFields = true;
                cleanedText = cleanedText.replace(new RegExp(singleTimeMatch[0], 'gi'), '');
            }
        }

        // Extract duration like "30 minutes" or "1 hour"
        const durationMatch = text.match(/(\d+\s*(?:minutes|min|hours|hrs?|hour))/i);
        if (durationMatch) {
            result.duration = durationMatch[1].toLowerCase();
            result.hasMultipleFields = true;
            cleanedText = cleanedText.replace(new RegExp(durationMatch[0], 'gi'), '');
        }

        // Extract time of day keywords
        const timeOfDayMatch = text.match(/\b(morning|afternoon|evening|night|tonight)\b/i);
        if (timeOfDayMatch) {
            result.timeOfDay = timeOfDayMatch[1].toLowerCase();
            result.hasMultipleFields = true;
            cleanedText = cleanedText.replace(new RegExp(timeOfDayMatch[0], 'gi'), '');
        }

        // Remove priority keywords
        Object.keys(priorityPatterns).forEach(pattern => {
            cleanedText = cleanedText.replace(new RegExp(pattern, 'gi'), '');
        });

        // Remove schedule keywords
        Object.keys(schedulePatterns).forEach(pattern => {
            cleanedText = cleanedText.replace(new RegExp(pattern, 'gi'), '');
        });

        // Remove common command words and filler phrases
        cleanedText = cleanedText.replace(/\b(create|add|schedule|set up|remind me to|remind me|plan|make|do|a|the|task|my|for|to|please)\b/gi, ' ');
        cleanedText = cleanedText.replace(/\s+/g, ' ').trim();

        const titlePhraseMatch = cleanedText.match(/(?:to\s+|for\s+)?(.+)$/i);
        let titleText = titlePhraseMatch ? titlePhraseMatch[1].trim() : cleanedText;

        if (titleText && titleText.length > 0) {
            result.title = titleText;
            result.hasMultipleFields = true;
        }

        result.description = this.buildDescription(result, transcript);
        if (result.description) {
            result.hasMultipleFields = true;
        }

        console.log('Parsed task:', result);
        return result;
    }

    extractDescription(transcript, title) {
        let description = transcript.trim();
        const lower = transcript.toLowerCase();
        const separators = [' details ', ' detail ', ' about ', ' note ', ' notes ', ' saying ', ' saying that ', ' and then ', ' then '];

        for (const sep of separators) {
            const idx = lower.indexOf(sep);
            if (idx !== -1) {
                description = transcript.slice(idx + sep.length).trim();
                break;
            }
        }

        if (title) {
            const normalizedTitle = title.toLowerCase();
            if (description.toLowerCase().startsWith(normalizedTitle)) {
                description = description.slice(normalizedTitle.length).trim();
            }
        }

        if (!description) {
            description = transcript.trim();
        }

        return description;
    }

    buildDescription(parsedTask, transcript) {
        const descriptionParts = [];

        if (parsedTask.duration) {
            descriptionParts.push(parsedTask.duration);
        }

        if (parsedTask.timeOfDay) {
            descriptionParts.push(parsedTask.timeOfDay);
        }

        if (parsedTask.recurrenceType === 'daily') {
            descriptionParts.push('daily');
        } else if (parsedTask.recurrenceType === 'once') {
            descriptionParts.push('once');
        } else if (parsedTask.recurrenceType === 'selective') {
            descriptionParts.push('on selected dates');
        }

        if (parsedTask.startTime) {
            descriptionParts.push(`starting at ${parsedTask.startTime}`);
        }

        if (parsedTask.endTime) {
            descriptionParts.push(`until ${parsedTask.endTime}`);
        }

        if (parsedTask.title) {
            descriptionParts.push(parsedTask.title);
        }

        let description = descriptionParts.join(' ').trim();
        if (!description || description.toLowerCase() === parsedTask.title?.toLowerCase()) {
            description = this.extractDescription(transcript, parsedTask.title);
        }

        if (description && parsedTask.title) {
            const cleaned = description.replace(new RegExp(this.escapeRegExp(parsedTask.title), 'i'), '').trim();
            if (cleaned) {
                description = cleaned;
            }
        }

        return description;
    }

    escapeRegExp(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    askForMissingFields(parsedTask) {
        if (!parsedTask.title) {
            this.askFollowupQuestion('I did not hear a task title. Please say the task title now.', answer => {
                parsedTask.title = answer.trim();
                if (parsedTask.title) {
                    this.fillMultipleFields(parsedTask);
                }
            });
            return;
        }

        if (!parsedTask.recurrenceType) {
            this.askFollowupQuestion('Please say the schedule type: once, daily, or selective. Say default for once.', answer => {
                const schedule = this.parseScheduleAnswer(answer);
                parsedTask.recurrenceType = schedule || 'once';
                parsedTask.hasMultipleFields = true;
                this.fillMultipleFields(parsedTask);
            });
            return;
        }

        if (!parsedTask.priority) {
            this.askFollowupQuestion('What priority should this task have? Say low, normal, should do, or very important. Say default for normal.', answer => {
                const priority = this.parsePriorityAnswer(answer);
                parsedTask.priority = priority || 'normal';
                parsedTask.hasMultipleFields = true;
                this.fillMultipleFields(parsedTask);
            });
            return;
        }

        if (!parsedTask.dueDate) {
            // Only ask for due date if the task is a one-time or selective task
            if (parsedTask.recurrenceType === 'once' || parsedTask.recurrenceType === 'selective') {
                this.askFollowupQuestion('Please say the start date for the task, like today, tomorrow, or April twelfth. Say default for today.', answer => {
                    parsedTask.dueDate = this.extractDateFromText(answer) || this.formatDateValue(new Date());
                    parsedTask.hasMultipleFields = true;
                    this.fillMultipleFields(parsedTask);
                });
            }
        }
    }

    askFollowupQuestion(promptText, callback) {
        if (!window.speechSynthesis) {
            const answer = window.prompt(promptText);
            if (answer !== null) callback(answer);
            return;
        }

        this.currentTarget = null;
        this.followupCallback = callback;

        // Start listening after the prompt finishes
        const utterance = new SpeechSynthesisUtterance(promptText);
        utterance.onend = () => {
            this.awaitingFollowup = true;
            this.recognition.start();
        };
        window.speechSynthesis.speak(utterance);
    }

    parseScheduleAnswer(answer) {
        const normalized = answer.toLowerCase();
        if (normalized.includes('daily') || normalized.includes('every day')) return 'daily';
        if (normalized.includes('selective') || normalized.includes('custom') || normalized.includes('specific')) return 'selective';
        if (normalized.includes('once') || normalized.includes('single')) return 'once';
        if (normalized.includes('default')) return 'once';
        return null;
    }

    parsePriorityAnswer(answer) {
        const normalized = answer.toLowerCase();
        if (normalized.includes('very important') || normalized.includes('high priority')) return 'very_important';
        if (normalized.includes('should do') || normalized.includes('important')) return 'should_do';
        if (normalized.includes('low')) return 'low';
        if (normalized.includes('normal') || normalized.includes('default')) return 'normal';
        return null;
    }

    extractDateFromText(text) {
        const normalized = text.toLowerCase();
        const today = new Date();

        if (normalized.includes('today') || normalized.includes('default')) {
            return this.formatDateValue(today);
        }
        if (normalized.includes('tomorrow')) {
            const tomorrow = new Date(today);
            tomorrow.setDate(today.getDate() + 1);
            return this.formatDateValue(tomorrow);
        }

        const weekdayMap = {
            sunday: 0,
            monday: 1,
            tuesday: 2,
            wednesday: 3,
            thursday: 4,
            friday: 5,
            saturday: 6
        };

        for (const [name, dayIndex] of Object.entries(weekdayMap)) {
            if (normalized.includes(name)) {
                const now = new Date(today);
                const offset = (dayIndex + 7 - now.getDay()) % 7 || 7;
                now.setDate(now.getDate() + offset);
                return this.formatDateValue(now);
            }
        }

        const dateMatch = normalized.match(/(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b)\s+(\d{1,2})/i);
        if (dateMatch) {
            const month = dateMatch[1];
            const day = parseInt(dateMatch[2], 10);
            const monthIndex = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].findIndex(m => month.startsWith(m));
            if (monthIndex >= 0) {
                const year = today.getFullYear();
                const parsed = new Date(year, monthIndex, day);
                if (!isNaN(parsed)) {
                    return this.formatDateValue(parsed);
                }
            }
        }

        return null;
    }

    parseTimeValue(value) {
        if (!value) return null;
        let normalized = value.trim().toLowerCase();
        const meridiemMatch = normalized.match(/\b(am|pm)\b/);
        let isPm = false;
        let isAm = false;
        if (meridiemMatch) {
            isPm = meridiemMatch[1] === 'pm';
            isAm = meridiemMatch[1] === 'am';
        }

        normalized = normalized.replace(/\s*(am|pm)\s*/i, '');
        let [hours, minutes] = normalized.split(':');
        hours = parseInt(hours, 10);
        minutes = minutes ? parseInt(minutes, 10) : 0;

        if (Number.isNaN(hours) || Number.isNaN(minutes)) return null;
        if (hours === 12 && isAm) {
            hours = 0;
        } else if (isPm && hours < 12) {
            hours += 12;
        }

        if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) return null;
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
    }

    formatDateValue(date) {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    }

    fillMultipleFields(parsedTask) {
        // Fill title field
        if (parsedTask.title) {
            const titleField = document.getElementById('title');
            if (titleField) {
                titleField.value = parsedTask.title;
                titleField.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }

        // Fill description field
        if (parsedTask.description) {
            const descriptionField = document.getElementById('description');
            if (descriptionField) {
                descriptionField.value = parsedTask.description;
                descriptionField.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }

        // Fill start time field
        if (parsedTask.startTime) {
            const startTimeField = document.getElementById('start_time');
            if (startTimeField) {
                startTimeField.value = parsedTask.startTime;
                startTimeField.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }

        // Fill end time field
        if (parsedTask.endTime) {
            const endTimeField = document.getElementById('end_time');
            if (endTimeField) {
                endTimeField.value = parsedTask.endTime;
                endTimeField.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }

        // Fill priority field
        if (parsedTask.priority) {
            const priorityField = document.getElementById('priority');
            if (priorityField) {
                priorityField.value = parsedTask.priority;
                priorityField.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }

        // Fill recurrence type field
        if (parsedTask.recurrenceType) {
            const recurrenceField = document.getElementById('recurrence_type');
            if (recurrenceField) {
                recurrenceField.value = parsedTask.recurrenceType;
                recurrenceField.dispatchEvent(new Event('change', { bubbles: true }));
                
                // Trigger recurrence option visibility
                this.updateRecurrenceOptions(parsedTask.recurrenceType);
            }
        }

        // Show summary notification
        const parts = [];
        if (parsedTask.title) parts.push(`Title: "${parsedTask.title}"`);
        if (parsedTask.priority) parts.push(`Priority: ${parsedTask.priority.replace('_', ' ')}`);
        if (parsedTask.recurrenceType) parts.push(`Schedule: ${parsedTask.recurrenceType}`);

        if (parts.length > 0) {
            showNotification(`✅ Auto-filled: ${parts.join(', ')}`, 'success');
        }
    }

    updateRecurrenceOptions(recurrenceType) {
        // Hide all recurrence options first
        const dailyOptions = document.getElementById('daily-options');
        const selectiveOptions = document.getElementById('selective-options');
        
        if (dailyOptions) dailyOptions.style.display = 'none';
        if (selectiveOptions) selectiveOptions.style.display = 'none';

        // Show relevant options based on selection
        if (recurrenceType === 'daily' && dailyOptions) {
            dailyOptions.style.display = 'block';
        } else if (recurrenceType === 'selective' && selectiveOptions) {
            selectiveOptions.style.display = 'block';
        }
    }

    insertText(text) {
        const targetElement = document.getElementById(this.currentTarget);

        if (!targetElement) return;

        // Get current cursor position or selection
        const start = targetElement.selectionStart;
        const end = targetElement.selectionEnd;
        const currentValue = targetElement.value;

        // Insert text at cursor position (or replace selection)
        const newValue = currentValue.substring(0, start) + text + currentValue.substring(end);
        targetElement.value = newValue;

        // Set cursor position after inserted text
        const newCursorPos = start + text.length;
        targetElement.setSelectionRange(newCursorPos, newCursorPos);
        targetElement.focus();

        // Trigger input event for any listeners
        targetElement.dispatchEvent(new Event('input', { bubbles: true }));
    }

    onRecognitionEnd() {
        this.isListening = false;

        // Reset button state
        const voiceButtons = document.querySelectorAll('.voice-btn');
        voiceButtons.forEach(button => {
            button.classList.remove('listening');
            button.textContent = '🎤';
            button.title = 'Voice to text';
        });

        console.log('Voice recognition ended');
    }

    onRecognitionError(event) {
        this.isListening = false;

        console.error('Speech recognition error:', event.error);

        let errorMessage = 'Voice input error occurred.';

        switch (event.error) {
            case 'no-speech':
                errorMessage = 'No speech was detected. Please try again.';
                break;
            case 'audio-capture':
                errorMessage = 'No microphone was found. Ensure microphone access is granted.';
                break;
            case 'not-allowed':
                errorMessage = 'Microphone access denied. Please allow microphone access and try again.';
                break;
            case 'network':
                errorMessage = 'Network error occurred. Please check your connection.';
                break;
            case 'service-not-allowed':
                errorMessage = 'Speech recognition service not allowed.';
                break;
        }

        showNotification(errorMessage, 'error');

        // Reset button state
        const voiceButtons = document.querySelectorAll('.voice-btn');
        voiceButtons.forEach(button => {
            button.classList.remove('listening');
            button.textContent = '🎤';
            button.title = 'Voice to text';
        });
    }

    hideVoiceButtons() {
        const voiceButtons = document.querySelectorAll('.voice-btn');
        voiceButtons.forEach(button => {
            button.style.display = 'none';
        });
    }

    speak(message) {
        if (!window.speechSynthesis) return;
        const utterance = new SpeechSynthesisUtterance(message);
        utterance.lang = 'en-US';
        window.speechSynthesis.speak(utterance);
    }
}

// Initialize voice input when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize voice input manager
    window.voiceInputManager = new VoiceInputManager();
});
