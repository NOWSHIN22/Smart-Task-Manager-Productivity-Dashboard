import sys
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTabWidget,
                             QProgressBar, QTextEdit, QFileDialog, QMessageBox, QCheckBox,
                             QSpinBox, QDialog, QFormLayout, QGroupBox, QStackedWidget,
                             QFrame, QSizePolicy, QGraphicsDropShadowEffect, QSlider,
                             QScrollArea)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPainter, QPen, QBrush, QLinearGradient
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import math

# Enhanced Database Handler with working CRUD operations
class DatabaseHandler:
    def __init__(self, host=None, user=None, password=None, database=None):
        # Using in-memory storage for demo purposes
        self.tasks = [
            [1, "Complete project proposal", "2024-02-15", "High", "Work", "pending", "Pending", "Important project deadline", "2024-02-10", "2024-02-15"],
            [2, "Review code changes", "2024-02-12", "Medium", "Development", "pending", "Pending", "Code review for new features", "2024-02-11", "2024-02-12"],
            [3, "Team meeting", "2024-02-13", "High", "Meeting", "completed", "Completed", "Weekly team sync", "2024-02-13", "2024-02-13"],
            [4, "Update documentation", "2024-02-14", "Low", "Documentation", "pending", "Pending", "Update user manual", "2024-02-14", "2024-02-14"],
            [5, "Prepare presentation", "2024-02-16", "High", "Work", "pending", "Pending", "Quarterly review presentation", "2024-02-15", "2024-02-16"],
        ]
        self.next_id = 6
        self.settings = {
            'work_duration': '25',
            'break_duration': '5',
            'long_break_duration': '15'
        }
    
    def connect(self):
        return True
    
    def create_tables(self):
        return True
    
    def get_tasks(self, condition=None, params=None):
        return [tuple(task) for task in self.tasks]
    
    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task[0] == task_id:
                return tuple(task)
        return None
    
    def add_task(self, task_data):
        try:
            new_task = [self.next_id] + list(task_data)
            self.tasks.append(new_task)
            self.next_id += 1
            return True
        except Exception as e:
            print(f"Error adding task: {e}")
            return False
    
    def update_task(self, task_id, task_data):
        try:
            for i, task in enumerate(self.tasks):
                if task[0] == task_id:
                    # Keep the ID and update the rest
                    self.tasks[i] = [task_id] + list(task_data)
                    return True
            return False
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
    
    def delete_task(self, task_id):
        try:
            for i, task in enumerate(self.tasks):
                if task[0] == task_id:
                    del self.tasks[i]
                    return True
            return False
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    def get_setting(self, setting_name):
        return self.settings.get(setting_name, '25')
    
    def update_setting(self, setting_name, value):
        self.settings[setting_name] = value
        return True

# Custom Circular Progress Widget
class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 350)  # Increased size
        self._value = 0
        self._maximum = 100
        self._text = ""
        self._color = QColor(234, 67, 53)  # Red for work
        self._background_color = QColor(240, 240, 240)
        self._text_color = QColor(60, 60, 60)
        
    def setValue(self, value):
        self._value = max(0, min(value, self._maximum))
        self.update()
    
    def setMaximum(self, maximum):
        self._maximum = maximum
        self.update()
    
    def setText(self, text):
        self._text = text
        self.update()
    
    def setColor(self, color):
        self._color = color
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate geometry
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 25
        
        # Draw background circle
        painter.setPen(QPen(self._background_color, 10))
        painter.drawEllipse(center.x() - radius, center.y() - radius, 
                          radius * 2, radius * 2)
        
        # Draw progress arc
        if self._maximum > 0:
            progress_angle = int(360 * self._value / self._maximum)
            painter.setPen(QPen(self._color, 10, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(center.x() - radius, center.y() - radius,
                          radius * 2, radius * 2, 90 * 16, -progress_angle * 16)
        
        # Draw text
        painter.setPen(self._text_color)
        font = QFont("Arial", 32, QFont.Bold)  # Increased font size
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, self._text)

# Enhanced Task Card Widget
class TaskCard(QFrame):
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.parent_widget = parent
        self.setupUI()
        self.setupShadow()
    
    def setupUI(self):
        self.setFixedHeight(180)  # Increased height
        self.setStyleSheet("""
            TaskCard {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #e0e0e0;
            }
            TaskCard:hover {
                border: 2px solid #4285f4;
                transform: translateY(-2px);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Increased padding
        layout.setSpacing(12)  # Increased spacing
        
        # Title and priority
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.task_data[1])
        title_label.setFont(QFont("Arial", 18, QFont.Bold))  # Increased font size
        title_label.setStyleSheet("color: #333;")
        
        priority_label = QLabel(self.task_data[3])
        priority_colors = {
            "High": "#ea4335",
            "Medium": "#fbbc05", 
            "Low": "#34a853"
        }
        priority_label.setStyleSheet(f"""
            background-color: {priority_colors.get(self.task_data[3], '#666')};
            color: white;
            padding: 6px 15px;
            border-radius: 15px;
            font-size: 14px;
            font-weight: bold;
        """)
        priority_label.setMaximumWidth(100)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(priority_label)
        
        # Description
        desc_label = QLabel(self.task_data[7][:80] + "..." if len(self.task_data[7]) > 80 else self.task_data[7])
        desc_label.setStyleSheet("color: #666; font-size: 15px;")  # Increased font size
        desc_label.setWordWrap(True)
        
        # Due date and status
        footer_layout = QHBoxLayout()
        
        due_date_label = QLabel(f"📅 Due: {self.task_data[2]}")
        due_date_label.setStyleSheet("color: #666; font-size: 15px;")  # Increased font size
        
        status_label = QLabel(self.task_data[6])
        status_color = "#34a853" if self.task_data[6] == "Completed" else "#fbbc05"
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold; font-size: 15px;")  # Increased font size
        
        footer_layout.addWidget(due_date_label)
        footer_layout.addWidget(status_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        complete_btn = QPushButton("✅ Complete")
        complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d8f3f;
            }
        """)
        complete_btn.clicked.connect(self.complete_task)
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        edit_btn.clicked.connect(self.edit_task)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ea4335;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d33b2c;
            }
        """)
        delete_btn.clicked.connect(self.delete_task)
        
        button_layout.addWidget(complete_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(desc_label)
        layout.addLayout(footer_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setupShadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def complete_task(self):
        # Find the main window through parent hierarchy
        main_window = self.get_main_window()
        if main_window:
            main_window.mark_task_completed_by_id(self.task_data[0])
    
    def edit_task(self):
        main_window = self.get_main_window()
        if main_window:
            main_window.edit_task_by_id(self.task_data[0])
    
    def delete_task(self):
        main_window = self.get_main_window()
        if main_window:
            main_window.delete_task_by_id(self.task_data[0])
    
    def get_main_window(self):
        widget = self
        while widget:
            if isinstance(widget, SmartTaskManager):
                return widget
            widget = widget.parent()
        return None

# Statistics Card Widget
class StatCard(QFrame):
    def __init__(self, title, value, icon, color):
        super().__init__()
        self.setupUI(title, value, icon, color)
    
    def setupUI(self, title, value, icon, color):
        self.setFixedHeight(120)  # Increased height
        self.setStyleSheet(f"""
            StatCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {color}CC);
                border-radius: 15px;
                border: none;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Icon and title
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px; color: white;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
    
    def update_value(self, new_value):
        self.value_label.setText(new_value)

# Enhanced Smart Task Manager
class SmartTaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Task Manager & Productivity Dashboard")
        self.setGeometry(100, 100, 1600, 1000)  # Increased window size
        
        # Set larger default font
        font = QFont()
        font.setPointSize(14)  # Increased base font size
        self.setFont(font)
        
        # Enhanced styling with larger fonts
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.7);
                border: none;
                padding: 15px 25px;
                margin-right: 3px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: bold;
                color: #666;
                font-size: 16px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #4285f4;
                border-bottom: 4px solid #4285f4;
            }
            QTabBar::tab:hover {
                background: rgba(66, 133, 244, 0.1);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4285f4, stop:1 #3367d6);
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 120px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3367d6, stop:1 #2a56c6);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: #2a56c6;
            }
            QPushButton:disabled {
                background: #cccccc;
            }
            QGroupBox {
                background: white;
                border: none;
                border-radius: 15px;
                margin-top: 20px;
                padding-top: 25px;
                font-weight: bold;
                font-size: 18px;
                color: #333;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {
                border: 2px solid #e0e0e0;
                padding: 12px;
                border-radius: 8px;
                background: white;
                font-size: 16px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, 
            QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus {
                border-color: #4285f4;
                outline: none;
            }
            QProgressBar {
                border: none;
                border-radius: 12px;
                background-color: #e0e0e0;
                height: 30px;
                text-align: center;
                font-weight: bold;
                font-size: 16px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4285f4, stop:1 #34a853);
                border-radius: 12px;
            }
            QLabel {
                font-size: 16px;
            }
        """)
        
        try:
            self.db = DatabaseHandler()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not initialize database. Using demo mode.\n{str(e)}")
            self.db = DatabaseHandler()
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create all tabs
        self.create_task_management_tab()
        self.create_dashboard_tab()
        self.create_pomodoro_tab()
        self.create_settings_tab()
        
        # Load initial data
        self.load_tasks()
        self.update_dashboard()
        
        # Initialize Pomodoro timer
        self.setup_pomodoro_timer()
        
    def create_task_management_tab(self):
        self.task_tab = QWidget()
        self.tabs.addTab(self.task_tab, "📝 Tasks")
        
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(25, 25, 25, 25)
        self.task_tab.setLayout(layout)
        
        # Enhanced Task Controls
        controls_group = QGroupBox("Quick Actions")
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        
        self.add_task_btn = QPushButton("➕ Add New Task")
        self.add_task_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34a853, stop:1 #2d8f3f);
                padding: 18px;
                font-size: 16px;
            }
        """)
        self.add_task_btn.clicked.connect(self.show_add_task_dialog)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fbbc05, stop:1 #f9ab00);
                padding: 18px;
                font-size: 16px;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_tasks)
        
        controls_layout.addWidget(self.add_task_btn)
        controls_layout.addWidget(self.refresh_btn)
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        
        # Enhanced Search and Filter
        filter_group = QGroupBox("Search & Filter")
        search_filter_layout = QHBoxLayout()
        search_filter_layout.setSpacing(20)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search tasks by title, description, or category...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.search_tasks)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "📋 All Tasks", "⏳ Pending", "✅ Completed", 
            "🔴 High Priority", "🟡 Medium Priority", "🟢 Low Priority", 
            "⚠️ Overdue", "📅 Due Today"
        ])
        self.filter_combo.currentIndexChanged.connect(self.filter_tasks)
        
        search_filter_layout.addWidget(self.search_input, 3)
        search_filter_layout.addWidget(self.filter_combo, 1)
        filter_group.setLayout(search_filter_layout)
        
        # Task Cards Container with Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.tasks_scroll_widget = QWidget()
        self.tasks_layout = QVBoxLayout()
        self.tasks_scroll_widget.setLayout(self.tasks_layout)
        scroll_area.setWidget(self.tasks_scroll_widget)
        
        layout.addWidget(controls_group)
        layout.addWidget(filter_group)
        layout.addWidget(scroll_area, 1)
    
    def create_dashboard_tab(self):
        self.dashboard_tab = QWidget()
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(25, 25, 25, 25)
        self.dashboard_tab.setLayout(layout)
        
        # Statistics Cards
        stats_group = QGroupBox("Task Statistics")
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_tasks_card = StatCard("Total Tasks", "0", "📋", "#4285f4")
        self.completed_tasks_card = StatCard("Completed", "0", "✅", "#34a853")
        self.pending_tasks_card = StatCard("Pending", "0", "⏳", "#fbbc05")
        self.overdue_tasks_card = StatCard("Overdue", "0", "⚠️", "#ea4335")
        
        stats_layout.addWidget(self.total_tasks_card)
        stats_layout.addWidget(self.completed_tasks_card)
        stats_layout.addWidget(self.pending_tasks_card)
        stats_layout.addWidget(self.overdue_tasks_card)
        stats_group.setLayout(stats_layout)
        
        # Progress Section
        progress_group = QGroupBox("Overall Progress")
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(15)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)
        
        layout.addWidget(stats_group)
        layout.addWidget(progress_group)
        layout.addStretch()
    
    def create_pomodoro_tab(self):
        self.pomodoro_tab = QWidget()
        self.tabs.addTab(self.pomodoro_tab, "🍅 Pomodoro")
        
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setAlignment(Qt.AlignCenter)
        self.pomodoro_tab.setLayout(layout)
        
        # Pomodoro Timer
        timer_group = QGroupBox("Pomodoro Timer")
        timer_layout = QVBoxLayout()
        timer_layout.setAlignment(Qt.AlignCenter)
        timer_layout.setSpacing(20)
        
        self.circular_progress = CircularProgress()
        timer_layout.addWidget(self.circular_progress, 0, Qt.AlignCenter)
        
        # Timer Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        self.start_timer_btn = QPushButton("▶️ Start")
        self.start_timer_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34a853, stop:1 #2d8f3f);
                padding: 15px 30px;
                font-size: 18px;
            }
        """)
        self.start_timer_btn.clicked.connect(self.start_pomodoro)
        
        self.pause_timer_btn = QPushButton("⏸️ Pause")
        self.pause_timer_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fbbc05, stop:1 #f9ab00);
                padding: 15px 30px;
                font-size: 18px;
            }
        """)
        self.pause_timer_btn.clicked.connect(self.pause_pomodoro)
        
        self.stop_timer_btn = QPushButton("⏹️ Stop")
        self.stop_timer_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ea4335, stop:1 #d33b2c);
                padding: 15px 30px;
                font-size: 18px;
            }
        """)
        self.stop_timer_btn.clicked.connect(self.stop_pomodoro)
        
        controls_layout.addWidget(self.start_timer_btn)
        controls_layout.addWidget(self.pause_timer_btn)
        controls_layout.addWidget(self.stop_timer_btn)
        
        timer_layout.addLayout(controls_layout)
        timer_group.setLayout(timer_layout)
        
        layout.addWidget(timer_group)
    
    def create_settings_tab(self):
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")
        
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(25, 25, 25, 25)
        self.settings_tab.setLayout(layout)
        
        # Pomodoro Settings
        pomodoro_group = QGroupBox("Pomodoro Timer Settings")
        pomodoro_layout = QFormLayout()
        pomodoro_layout.setLabelAlignment(Qt.AlignRight)
        pomodoro_layout.setVerticalSpacing(15)
        
        self.work_duration_spin = QSpinBox()
        self.work_duration_spin.setRange(1, 60)
        self.work_duration_spin.setValue(int(self.db.get_setting('work_duration')))
        self.work_duration_spin.setSuffix(" minutes")
        # Connect to real-time update
        self.work_duration_spin.valueChanged.connect(self.on_work_duration_changed)
        
        self.break_duration_spin = QSpinBox()
        self.break_duration_spin.setRange(1, 30)
        self.break_duration_spin.setValue(int(self.db.get_setting('break_duration')))
        self.break_duration_spin.setSuffix(" minutes")
        # Connect to real-time update
        self.break_duration_spin.valueChanged.connect(self.on_break_duration_changed)
        
        self.long_break_duration_spin = QSpinBox()
        self.long_break_duration_spin.setRange(1, 60)
        self.long_break_duration_spin.setValue(int(self.db.get_setting('long_break_duration')))
        self.long_break_duration_spin.setSuffix(" minutes")
        # Connect to real-time update
        self.long_break_duration_spin.valueChanged.connect(self.on_long_break_duration_changed)
        
        pomodoro_layout.addRow("Work Duration:", self.work_duration_spin)
        pomodoro_layout.addRow("Break Duration:", self.break_duration_spin)
        pomodoro_layout.addRow("Long Break Duration:", self.long_break_duration_spin)
        
        save_settings_btn = QPushButton("💾 Save Settings")
        save_settings_btn.clicked.connect(self.save_settings)
        pomodoro_layout.addRow("", save_settings_btn)
        
        # Add info label
        info_label = QLabel("💡 Settings are applied immediately to the timer!")
        info_label.setStyleSheet("color: #4285f4; font-style: italic; margin-top: 10px;")
        pomodoro_layout.addRow("", info_label)
        
        pomodoro_group.setLayout(pomodoro_layout)
        layout.addWidget(pomodoro_group)
        layout.addStretch()
    
    def on_work_duration_changed(self, value):
        """Called when work duration setting changes"""
        self.db.update_setting('work_duration', str(value))
        self.update_timer_for_settings_change()
    
    def on_break_duration_changed(self, value):
        """Called when break duration setting changes"""
        self.db.update_setting('break_duration', str(value))
        self.update_timer_for_settings_change()
    
    def on_long_break_duration_changed(self, value):
        """Called when long break duration setting changes"""
        self.db.update_setting('long_break_duration', str(value))
        self.update_timer_for_settings_change()
    
    def update_timer_for_settings_change(self):
        """Update the current timer when settings change"""
        # If timer is not running and not started, update the display
        if not self.is_timer_running and self.timer_remaining == 0:
            # Reset to new work duration
            work_duration = int(self.db.get_setting('work_duration'))
            self.timer_duration = work_duration * 60
            self.circular_progress.setMaximum(self.timer_duration)
            self.circular_progress.setValue(0)
            minutes = work_duration
            self.circular_progress.setText(f"{minutes:02d}:00")
        
        # If timer is currently running or paused, adjust the current session
        elif self.timer_remaining > 0:
            if self.is_work_session:
                # Update work session with new duration
                new_duration = int(self.db.get_setting('work_duration')) * 60
                # Calculate how much time has passed
                elapsed_time = self.timer_duration - self.timer_remaining
                
                # If the new duration is longer than elapsed time, extend the session
                if new_duration > elapsed_time:
                    self.timer_duration = new_duration
                    self.timer_remaining = new_duration - elapsed_time
                    self.circular_progress.setMaximum(self.timer_duration)
                    
                    # Update display
                    minutes = self.timer_remaining // 60
                    seconds = self.timer_remaining % 60
                    self.circular_progress.setText(f"{minutes:02d}:{seconds:02d}")
                    
                    # Update progress
                    self.circular_progress.setValue(elapsed_time)
                else:
                    # If new duration is shorter and already exceeded, complete the session
                    if elapsed_time >= new_duration:
                        self.timer_remaining = 0
                        self.update_timer()  # This will trigger session completion
            else:
                # Update break session with new duration
                new_duration = int(self.db.get_setting('break_duration')) * 60
                elapsed_time = self.timer_duration - self.timer_remaining
                
                if new_duration > elapsed_time:
                    self.timer_duration = new_duration
                    self.timer_remaining = new_duration - elapsed_time
                    self.circular_progress.setMaximum(self.timer_duration)
                    
                    # Update display
                    minutes = self.timer_remaining // 60
                    seconds = self.timer_remaining % 60
                    self.circular_progress.setText(f"{minutes:02d}:{seconds:02d}")
                    
                    # Update progress
                    self.circular_progress.setValue(elapsed_time)
                else:
                    # If new duration is shorter and already exceeded, complete the session
                    if elapsed_time >= new_duration:
                        self.timer_remaining = 0
                        self.update_timer()  # This will trigger session completion
        
        # Show notification about the change
        QMessageBox.information(self, "Settings Updated", 
                              "⚡ Timer settings have been updated and applied to the current session!")
    
    def setup_pomodoro_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer_duration = 0
        self.timer_remaining = 0
        self.is_work_session = True
        self.is_timer_running = False
        
        # Initialize circular progress with current work duration
        work_duration = int(self.db.get_setting('work_duration'))
        self.circular_progress.setText(f"{work_duration:02d}:00")
        self.circular_progress.setMaximum(work_duration * 60)
        self.circular_progress.setValue(0)
    
    def start_pomodoro(self):
        if not self.is_timer_running:
            if self.timer_remaining == 0:
                # Start new session with current settings
                if self.is_work_session:
                    duration = int(self.db.get_setting('work_duration'))
                    self.circular_progress.setColor(QColor(234, 67, 53))  # Red for work
                else:
                    duration = int(self.db.get_setting('break_duration'))
                    self.circular_progress.setColor(QColor(52, 168, 83))  # Green for break
                
                self.timer_duration = duration * 60
                self.timer_remaining = self.timer_duration
                self.circular_progress.setMaximum(self.timer_duration)
            
            self.is_timer_running = True
            self.timer.start(1000)  # Update every second
            
            self.start_timer_btn.setText("▶️ Resume" if self.timer_remaining < self.timer_duration else "▶️ Start")
            self.start_timer_btn.setEnabled(False)
            self.pause_timer_btn.setEnabled(True)
    
    def pause_pomodoro(self):
        if self.is_timer_running:
            self.timer.stop()
            self.is_timer_running = False
            self.start_timer_btn.setEnabled(True)
            self.pause_timer_btn.setEnabled(False)
    
    def stop_pomodoro(self):
        self.timer.stop()
        self.is_timer_running = False
        self.timer_remaining = 0
        self.circular_progress.setValue(0)
        
        # Reset to work session and current work duration
        self.is_work_session = True
        work_duration = int(self.db.get_setting('work_duration'))
        self.circular_progress.setText(f"{work_duration:02d}:00")
        self.circular_progress.setColor(QColor(234, 67, 53))  # Red for work
        
        self.start_timer_btn.setText("▶️ Start")
        self.start_timer_btn.setEnabled(True)
        self.pause_timer_btn.setEnabled(False)
    
    def update_timer(self):
        if self.timer_remaining > 0:
            self.timer_remaining -= 1
            
            # Update circular progress
            elapsed = self.timer_duration - self.timer_remaining
            self.circular_progress.setValue(elapsed)
            
            # Update time display
            minutes = self.timer_remaining // 60
            seconds = self.timer_remaining % 60
            self.circular_progress.setText(f"{minutes:02d}:{seconds:02d}")
        else:
            # Timer finished
            self.timer.stop()
            self.is_timer_running = False
            
            if self.is_work_session:
                QMessageBox.information(self, "Pomodoro Complete!", "Great work! Time for a break! 🎉")
                # Switch to break with current break duration
                break_duration = int(self.db.get_setting('break_duration'))
                self.timer_duration = break_duration * 60
                self.timer_remaining = self.timer_duration
                self.circular_progress.setMaximum(self.timer_duration)
                self.circular_progress.setColor(QColor(52, 168, 83))  # Green for break
                self.is_work_session = False
            else:
                QMessageBox.information(self, "Break Complete!", "Break's over! Ready to get back to work? 💪")
                # Switch back to work with current work duration
                work_duration = int(self.db.get_setting('work_duration'))
                self.timer_duration = work_duration * 60
                self.timer_remaining = work_duration * 60
                self.circular_progress.setMaximum(self.timer_duration)
                self.circular_progress.setColor(QColor(234, 67, 53))  # Red for work
                self.is_work_session = True
            
            self.start_timer_btn.setText("▶️ Start")
            self.start_timer_btn.setEnabled(True)
            self.pause_timer_btn.setEnabled(False)
    
    def save_settings(self):
        try:
            # Settings are already saved via the valueChanged signals
            # This button now just shows a confirmation
            QMessageBox.information(self, "Settings Saved", 
                                  "✅ All Pomodoro timer settings have been saved and are active!\n\n"
                                  "📝 Note: Settings are automatically applied when you change them.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")
    
    def load_tasks(self):
        # Clear existing task cards
        for i in reversed(range(self.tasks_layout.count())):
            child = self.tasks_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Load tasks from database
        tasks = self.db.get_tasks()
        
        if not tasks:
            no_tasks_label = QLabel("📝 No tasks found. Click 'Add New Task' to get started!")
            no_tasks_label.setStyleSheet("""
                color: #666;
                font-size: 20px;
                padding: 50px;
                text-align: center;
                background: white;
                border-radius: 15px;
                border: 3px dashed #ddd;
            """)
            no_tasks_label.setAlignment(Qt.AlignCenter)
            self.tasks_layout.addWidget(no_tasks_label)
        else:
            for task in tasks:
                task_card = TaskCard(task, self.tasks_scroll_widget)
                self.tasks_layout.addWidget(task_card)
        
        self.tasks_layout.addStretch()
        self.update_dashboard()
    
    def update_dashboard(self):
        tasks = self.db.get_tasks()
        
        if not tasks:
            self.total_tasks_card.update_value("0")
            self.completed_tasks_card.update_value("0 (0%)")
            self.pending_tasks_card.update_value("0 (0%)")
            self.overdue_tasks_card.update_value("0 (0%)")
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("No tasks yet")
            return
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t[6] == "Completed"])
        pending_tasks = len([t for t in tasks if t[6] == "Pending"])
        
        # Calculate overdue tasks
        today = datetime.now().date()
        overdue_tasks = 0
        for task in tasks:
            if task[6] == "Pending":
                try:
                    due_date = datetime.strptime(task[2], "%Y-%m-%d").date()
                    if due_date < today:
                        overdue_tasks += 1
                except:
                    pass
        
        # Update stat cards
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        pending_rate = (pending_tasks / total_tasks * 100) if total_tasks > 0 else 0
        overdue_rate = (overdue_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        self.total_tasks_card.update_value(str(total_tasks))
        self.completed_tasks_card.update_value(f"{completed_tasks} ({completion_rate:.0f}%)")
        self.pending_tasks_card.update_value(f"{pending_tasks} ({pending_rate:.0f}%)")
        self.overdue_tasks_card.update_value(f"{overdue_tasks} ({overdue_rate:.0f}%)")
        
        # Update progress bar
        self.progress_bar.setValue(int(completion_rate))
        self.progress_bar.setFormat(f"{completion_rate:.0f}% Complete - {'Excellent!' if completion_rate >= 80 else 'Keep going!' if completion_rate >= 50 else 'You can do it!'}")
    
    def mark_task_completed_by_id(self, task_id):
        task = self.db.get_task_by_id(task_id)
        if task and task[6] == "Pending":
            task_data = (
                task[1], task[2], task[3], task[4], 
                task[5], "Completed", task[7], task[8], task[9]
            )
            if self.db.update_task(task_id, task_data):
                self.load_tasks()
                QMessageBox.information(self, "Success", "Task marked as completed! 🎉")
            else:
                QMessageBox.warning(self, "Error", "Failed to update task")
        else:
            QMessageBox.information(self, "Info", "Task is already completed or not found")
    
    def edit_task_by_id(self, task_id):
        task = self.db.get_task_by_id(task_id)
        if task:
            self.show_edit_task_dialog(task)
        else:
            QMessageBox.warning(self, "Error", "Task not found")
    
    def delete_task_by_id(self, task_id):
        task = self.db.get_task_by_id(task_id)
        if task:
            reply = QMessageBox.question(
                self, 
                "Confirm Deletion", 
                f"Are you sure you want to delete task '{task[1]}'?\n\nThis action cannot be undone.", 
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.db.delete_task(task_id):
                    self.load_tasks()
                    QMessageBox.information(self, "Success", "Task deleted successfully! 🗑️")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete task")
        else:
            QMessageBox.warning(self, "Error", "Task not found")
    
    def show_add_task_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Task")
        dialog.setFixedSize(600, 700)  # Increased size
        dialog.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("✨ Add New Task")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Form fields
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setVerticalSpacing(20)
        
        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter task title")
        form.addRow("Task Title:", self.title_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter task description")
        self.description_input.setMaximumHeight(120)
        form.addRow("Description:", self.description_input)
        
        # Due Date
        self.due_date_input = QDateEdit()
        self.due_date_input.setDate(QDate.currentDate().addDays(1))
        self.due_date_input.setCalendarPopup(True)
        form.addRow("Due Date:", self.due_date_input)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        self.priority_combo.setCurrentText("Medium")
        form.addRow("Priority:", self.priority_combo)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Work", "Personal", "Study", "Health", "Other"])
        form.addRow("Category:", self.category_combo)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Completed"])
        form.addRow("Status:", self.status_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_btn = QPushButton("💾 Save Task")
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34a853, stop:1 #2d8f3f);
                padding: 15px 30px;
                font-size: 16px;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_new_task(dialog))
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ea4335, stop:1 #d33b2c);
                padding: 15px 30px;
                font-size: 16px;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(title_label)
        layout.addLayout(form)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        dialog.exec_()
    
    def show_edit_task_dialog(self, task):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Task")
        dialog.setFixedSize(600, 700)  # Increased size
        dialog.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel(f"✏️ Edit Task: {task[1]}")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Form fields
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setVerticalSpacing(20)
        
        # Title
        self.edit_title_input = QLineEdit(task[1])
        self.edit_title_input.setPlaceholderText("Enter task title")
        form.addRow("Task Title:", self.edit_title_input)
        
        # Description
        self.edit_description_input = QTextEdit(task[7])
        self.edit_description_input.setPlaceholderText("Enter task description")
        self.edit_description_input.setMaximumHeight(120)
        form.addRow("Description:", self.edit_description_input)
        
        # Due Date
        self.edit_due_date_input = QDateEdit()
        try:
            due_date = QDate.fromString(task[2], "yyyy-MM-dd")
            self.edit_due_date_input.setDate(due_date)
        except:
            self.edit_due_date_input.setDate(QDate.currentDate().addDays(1))
        self.edit_due_date_input.setCalendarPopup(True)
        form.addRow("Due Date:", self.edit_due_date_input)
        
        # Priority
        self.edit_priority_combo = QComboBox()
        self.edit_priority_combo.addItems(["High", "Medium", "Low"])
        self.edit_priority_combo.setCurrentText(task[3])
        form.addRow("Priority:", self.edit_priority_combo)
        
        # Category
        self.edit_category_combo = QComboBox()
        self.edit_category_combo.addItems(["Work", "Personal", "Study", "Health", "Other"])
        self.edit_category_combo.setCurrentText(task[4])
        form.addRow("Category:", self.edit_category_combo)
        
        # Status
        self.edit_status_combo = QComboBox()
        self.edit_status_combo.addItems(["Pending", "Completed"])
        self.edit_status_combo.setCurrentText(task[6])
        form.addRow("Status:", self.edit_status_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4285f4, stop:1 #3367d6);
                padding: 15px 30px;
                font-size: 16px;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_edited_task(task[0], dialog))
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ea4335, stop:1 #d33b2c);
                padding: 15px 30px;
                font-size: 16px;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(title_label)
        layout.addLayout(form)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        dialog.exec_()
    
    def save_new_task(self, dialog):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Task title is required!")
            return
        
        task_data = (
            title,
            self.due_date_input.date().toString("yyyy-MM-dd"),
            self.priority_combo.currentText(),
            self.category_combo.currentText(),
            "pending",  # internal status
            self.status_combo.currentText(),  # display status
            self.description_input.toPlainText(),
            datetime.now().strftime("%Y-%m-%d"),  # start_date
            self.due_date_input.date().toString("yyyy-MM-dd")  # end_date
        )
        
        if self.db.add_task(task_data):
            QMessageBox.information(self, "Success", "Task added successfully! ✨")
            dialog.accept()
            self.load_tasks()
        else:
            QMessageBox.warning(self, "Error", "Failed to add task")
    
    def save_edited_task(self, task_id, dialog):
        title = self.edit_title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Task title is required!")
            return
        
        task_data = (
            title,
            self.edit_due_date_input.date().toString("yyyy-MM-dd"),
            self.edit_priority_combo.currentText(),
            self.edit_category_combo.currentText(),
            "pending" if self.edit_status_combo.currentText() == "Pending" else "completed",
            self.edit_status_combo.currentText(),
            self.edit_description_input.toPlainText(),
            datetime.now().strftime("%Y-%m-%d"),  # start_date
            self.edit_due_date_input.date().toString("yyyy-MM-dd")  # end_date
        )
        
        if self.db.update_task(task_id, task_data):
            QMessageBox.information(self, "Success", "Task updated successfully! ✅")
            dialog.accept()
            self.load_tasks()
        else:
            QMessageBox.warning(self, "Error", "Failed to update task")
    
    def search_tasks(self):
        search_text = self.search_input.text().lower()
        filter_selection = self.filter_combo.currentText()
        self.apply_filters(search_text, filter_selection)
    
    def filter_tasks(self):
        search_text = self.search_input.text().lower()
        filter_selection = self.filter_combo.currentText()
        self.apply_filters(search_text, filter_selection)
    
    def apply_filters(self, search_text, filter_selection):
        # Clear existing task cards
        for i in reversed(range(self.tasks_layout.count())):
            child = self.tasks_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get all tasks
        all_tasks = self.db.get_tasks()
        filtered_tasks = []
        
        today = datetime.now().date()
        
        for task in all_tasks:
            # Apply search filter
            if search_text and search_text not in task[1].lower() and search_text not in task[7].lower() and search_text not in task[4].lower():
                continue
            
            # Apply status/priority filters
            if filter_selection == "📋 All Tasks":
                filtered_tasks.append(task)
            elif filter_selection == "⏳ Pending" and task[6] == "Pending":
                filtered_tasks.append(task)
            elif filter_selection == "✅ Completed" and task[6] == "Completed":
                filtered_tasks.append(task)
            elif filter_selection == "🔴 High Priority" and task[3] == "High":
                filtered_tasks.append(task)
            elif filter_selection == "🟡 Medium Priority" and task[3] == "Medium":
                filtered_tasks.append(task)
            elif filter_selection == "🟢 Low Priority" and task[3] == "Low":
                filtered_tasks.append(task)
            elif filter_selection == "⚠️ Overdue":
                try:
                    due_date = datetime.strptime(task[2], "%Y-%m-%d").date()
                    if due_date < today and task[6] == "Pending":
                        filtered_tasks.append(task)
                except:
                    pass
            elif filter_selection == "📅 Due Today":
                try:
                    due_date = datetime.strptime(task[2], "%Y-%m-%d").date()
                    if due_date == today:
                        filtered_tasks.append(task)
                except:
                    pass
        
        # Display filtered tasks
        if not filtered_tasks:
            no_tasks_label = QLabel(f"🔍 No tasks match your search criteria.\n\nTry adjusting your search or filter settings.")
            no_tasks_label.setStyleSheet("""
                color: #666;
                font-size: 18px;
                padding: 40px;
                text-align: center;
                background: white;
                border-radius: 15px;
                border: 2px dashed #ddd;
            """)
            no_tasks_label.setAlignment(Qt.AlignCenter)
            self.tasks_layout.addWidget(no_tasks_label)
        else:
            for task in filtered_tasks:
                task_card = TaskCard(task, self.tasks_scroll_widget)
                self.tasks_layout.addWidget(task_card)
        
        self.tasks_layout.addStretch()

def main():
    app = QApplication(sys.argv)
    
    # Set application style and properties
    app.setStyle('Fusion')
    app.setApplicationName("Smart Task Manager Pro")
    app.setApplicationVersion("2.1")
    app.setOrganizationName("Productivity Solutions")
    
    # Set larger default font
    font = QFont()
    font.setPointSize(14)  # Increased base font size
    app.setFont(font)
    
    try:
        window = SmartTaskManager()
        window.show()
        
        # Show welcome message
        welcome_msg = QMessageBox(window)
        welcome_msg.setWindowTitle("Welcome! 🎉")
        welcome_msg.setIcon(QMessageBox.Information)
        welcome_msg.setText("Welcome to Smart Task Manager Pro!")
        welcome_msg.setInformativeText(
            "✨ Features:\n"
            "• Fully functional task management with working edit/delete\n"
            "• Enhanced Pomodoro Timer with REAL-TIME settings updates\n"
            "• Real-time task analytics and dashboard\n"
            "• Advanced search and filtering\n"
            "• Larger, more readable fonts\n"
            "• Modern, responsive interface\n"
            "• Settings now automatically update the timer!\n\n"
            "🔥 NEW: Change timer settings and see them applied immediately!"
        )
        welcome_msg.setStandardButtons(QMessageBox.Ok)
        welcome_msg.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Application Error", f"Failed to start application:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
            