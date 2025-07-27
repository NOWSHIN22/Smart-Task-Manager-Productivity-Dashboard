import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTabWidget,
                             QProgressBar, QTextEdit, QFileDialog, QMessageBox, QCheckBox,
                             QSpinBox, QDialog, QFormLayout)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QIcon
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class SmartTaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Task Manager & Productivity Dashboard")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize database
        self.init_db()
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Task Management Tab
        self.create_task_management_tab()
        
        # Productivity Dashboard Tab
        self.create_dashboard_tab()
        
        # Settings Tab
        self.create_settings_tab()
        
        # Load initial data
        self.load_tasks()
        self.update_dashboard()
        
    def init_db(self):
        self.conn = sqlite3.connect('task_manager.db')
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                due_time TEXT,
                priority TEXT,
                status TEXT,
                category TEXT,
                recurrence TEXT,
                attachment_path TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS TaskHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                completion_date TEXT,
                FOREIGN KEY(task_id) REFERENCES Tasks(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserSettings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_name TEXT UNIQUE,
                setting_value TEXT
            )
        ''')
        
        self.conn.commit()
    
    def create_task_management_tab(self):
        self.task_tab = QWidget()
        self.tabs.addTab(self.task_tab, "Task Management")
        
        layout = QVBoxLayout()
        self.task_tab.setLayout(layout)
        
        # Task Controls
        controls_layout = QHBoxLayout()
        
        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.clicked.connect(self.show_add_task_dialog)
        
        self.edit_task_btn = QPushButton("Edit Task")
        self.edit_task_btn.clicked.connect(self.edit_task)
        
        self.delete_task_btn = QPushButton("Delete Task")
        self.delete_task_btn.clicked.connect(self.delete_task)
        
        controls_layout.addWidget(self.add_task_btn)
        controls_layout.addWidget(self.edit_task_btn)
        controls_layout.addWidget(self.delete_task_btn)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks...")
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_tasks)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        
        # Filter
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Pending", "Completed", "High Priority", "Medium Priority", "Low Priority"])
        self.filter_combo.currentIndexChanged.connect(self.filter_tasks)
        
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_combo)
        
        # Task Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels(["ID", "Title", "Due Date", "Priority", "Status", "Category"])
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Add to main layout
        layout.addLayout(controls_layout)
        layout.addLayout(search_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.task_table)
    
    def create_dashboard_tab(self):
        self.dashboard_tab = QWidget()
        self.tabs.addTab(self.dashboard_tab, "Productivity Dashboard")
        
        layout = QVBoxLayout()
        self.dashboard_tab.setLayout(layout)
        
        # Stats
        stats_layout = QHBoxLayout()
        
        self.total_tasks_label = QLabel("Total Tasks: 0")
        self.completed_tasks_label = QLabel("Completed: 0 (0%)")
        
        stats_layout.addWidget(self.total_tasks_label)
        stats_layout.addWidget(self.completed_tasks_label)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        
        # Charts
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        # Task Status Pie Chart
        self.status_chart = self.figure.add_subplot(121)
        self.status_chart.set_title("Task Status")
        
        # Priority Distribution Chart
        self.priority_chart = self.figure.add_subplot(122)
        self.priority_chart.set_title("Priority Distribution")
        
        # Add to main layout
        layout.addLayout(stats_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.canvas)
    
    def create_settings_tab(self):
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "Settings")
        
        layout = QVBoxLayout()
        self.settings_tab.setLayout(layout)
        
        # Backup/Restore
        backup_layout = QHBoxLayout()
        
        self.backup_btn = QPushButton("Backup Data")
        self.backup_btn.clicked.connect(self.backup_data)
        
        self.restore_btn = QPushButton("Restore Data")
        self.restore_btn.clicked.connect(self.restore_data)
        
        backup_layout.addWidget(self.backup_btn)
        backup_layout.addWidget(self.restore_btn)
        
        # Notification Settings
        notif_layout = QVBoxLayout()
        notif_layout.addWidget(QLabel("Notification Settings:"))
        
        self.email_notif_check = QCheckBox("Enable Daily Summary Email Notifications")
        self.desktop_notif_check = QCheckBox("Enable Desktop Notifications")
        
        notif_layout.addWidget(self.email_notif_check)
        notif_layout.addWidget(self.desktop_notif_check)
        
        # Pomodoro Settings
        pomodoro_layout = QVBoxLayout()
        pomodoro_layout.addWidget(QLabel("Pomodoro Timer Settings:"))
        
        work_layout = QHBoxLayout()
        work_layout.addWidget(QLabel("Work Duration (minutes):"))
        self.work_duration = QSpinBox()
        self.work_duration.setRange(5, 60)
        self.work_duration.setValue(25)
        work_layout.addWidget(self.work_duration)
        
        break_layout = QHBoxLayout()
        break_layout.addWidget(QLabel("Break Duration (minutes):"))
        self.break_duration = QSpinBox()
        self.break_duration.setRange(1, 30)
        self.break_duration.setValue(5)
        break_layout.addWidget(self.break_duration)
        
        pomodoro_layout.addLayout(work_layout)
        pomodoro_layout.addLayout(break_layout)
        
        # Add to main layout
        layout.addLayout(backup_layout)
        layout.addLayout(notif_layout)
        layout.addLayout(pomodoro_layout)
        layout.addStretch()
    
    def load_tasks(self):
        query = "SELECT id, title, due_date, priority, status, category FROM Tasks"
        self.cursor.execute(query)
        tasks = self.cursor.fetchall()
        
        self.task_table.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            for col, data in enumerate(task):
                self.task_table.setItem(row, col, QTableWidgetItem(str(data)))
    
    def update_dashboard(self):
        # Get task stats
        self.cursor.execute("SELECT COUNT(*) FROM Tasks")
        total_tasks = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM Tasks WHERE status='Completed'")
        completed_tasks = self.cursor.fetchone()[0]
        
        completion_percentage = 0
        if total_tasks > 0:
            completion_percentage = (completed_tasks / total_tasks) * 100
        
        # Update labels
        self.total_tasks_label.setText(f"Total Tasks: {total_tasks}")
        self.completed_tasks_label.setText(f"Completed: {completed_tasks} ({completion_percentage:.1f}%)")
        self.progress_bar.setValue(int(completion_percentage))
        
        # Update charts
        self.update_charts()
    
    def update_charts(self):
        # Clear previous charts
        self.status_chart.clear()
        self.priority_chart.clear()
        
        try:
            # Get data for charts
            status_data = {"Completed": 0, "Pending": 0}
            priority_data = {"High": 0, "Medium": 0, "Low": 0}
            
            # Get status counts
            self.cursor.execute("SELECT status, COUNT(*) FROM Tasks GROUP BY status")
            status_results = self.cursor.fetchall()
            for status, count in status_results:
                if status in status_data:
                    status_data[status] = count
            
            # Get priority counts
            self.cursor.execute("SELECT priority, COUNT(*) FROM Tasks GROUP BY priority")
            priority_results = self.cursor.fetchall()
            for priority, count in priority_results:
                if priority in priority_data:
                    priority_data[priority] = count
            
            # Only plot if we have data
            if any(status_data.values()):
                # Plot status pie chart
                self.status_chart.pie(
                    [v for v in status_data.values() if v > 0],
                    labels=[k for k, v in status_data.items() if v > 0],
                    autopct='%1.1f%%'
                )
                self.status_chart.set_title("Task Status")
            else:
                self.status_chart.text(0.5, 0.5, 'No task data', 
                                    ha='center', va='center')
            
            if any(priority_data.values()):
                # Plot priority bar chart
                self.priority_chart.bar(
                    [k for k, v in priority_data.items() if v > 0],
                    [v for k, v in priority_data.items() if v > 0]
                )
                self.priority_chart.set_title("Priority Distribution")
            else:
                self.priority_chart.text(0.5, 0.5, 'No task data', 
                                       ha='center', va='center')
            
            self.canvas.draw()
        
        except Exception as e:
            print(f"Error updating charts: {e}")
            # Display error message on charts if something goes wrong
            self.status_chart.clear()
            self.status_chart.text(0.5, 0.5, 'Chart error', 
                                 ha='center', va='center')
            self.priority_chart.clear()
            self.priority_chart.text(0.5, 0.5, 'Chart error', 
                                   ha='center', va='center')
            self.canvas.draw()
    
    def show_add_task_dialog(self):
        self.add_dialog = QDialog(self)  # Store dialog as instance variable
        self.add_dialog.setWindowTitle("Add New Task")
        self.add_dialog.setModal(True)
        
        layout = QVBoxLayout()
        
        # Form fields
        form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.description_input = QTextEdit()
        self.due_date_input = QDateEdit()
        self.due_date_input.setDate(QDate.currentDate())
        self.due_time_input = QTimeEdit()
        self.due_time_input.setTime(QTime.currentTime())
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Completed"])
        
        self.category_input = QLineEdit()
        
        self.recurrence_combo = QComboBox()
        self.recurrence_combo.addItems(["None", "Daily", "Weekly", "Monthly"])
        
        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Due Date:", self.due_date_input)
        form_layout.addRow("Due Time:", self.due_time_input)
        form_layout.addRow("Priority:", self.priority_combo)
        form_layout.addRow("Status:", self.status_combo)
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Recurrence:", self.recurrence_combo)
        
        # Attachment
        attachment_layout = QHBoxLayout()
        self.attachment_path = QLineEdit()
        self.attachment_path.setReadOnly(True)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_attachment(self.attachment_path))
        
        attachment_layout.addWidget(self.attachment_path)
        attachment_layout.addWidget(browse_btn)
        form_layout.addRow("Attachment:", attachment_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_task(self.add_dialog))
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.add_dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add to dialog
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.add_dialog.setLayout(layout)
        
        self.add_dialog.exec_()
    
    def browse_attachment(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Attachment")
        if file_path:
            line_edit.setText(file_path)
    
    def save_task(self, dialog):
        # Get all field values
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        due_date = self.due_date_input.date().toString("yyyy-MM-dd")
        due_time = self.due_time_input.time().toString("hh:mm")
        priority = self.priority_combo.currentText()
        status = self.status_combo.currentText()
        category = self.category_input.text()
        recurrence = self.recurrence_combo.currentText()
        attachment = self.attachment_path.text()
        
        # Validate
        if not title:
            QMessageBox.warning(self, "Warning", "Title is required!")
            return
        
        # Insert into database
        query = """
            INSERT INTO Tasks 
            (title, description, due_date, due_time, priority, status, category, recurrence, attachment_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.cursor.execute(query, (title, description, due_date, due_time, priority, 
                                      status, category, recurrence, attachment))
            self.conn.commit()
            
            # Refresh UI
            self.load_tasks()
            self.update_dashboard()
            
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save task:\n{str(e)}")
    
    def edit_task(self):
        selected = self.task_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a task to edit!")
            return
        
        task_id = selected[0].text()
        
        # Get task details from database
        query = "SELECT * FROM Tasks WHERE id = ?"
        self.cursor.execute(query, (task_id,))
        task = self.cursor.fetchone()
        
        if not task:
            QMessageBox.warning(self, "Error", "Task not found!")
            return
        
        # Create edit dialog
        self.edit_dialog = QDialog(self)  # Store dialog as instance variable
        self.edit_dialog.setWindowTitle("Edit Task")
        self.edit_dialog.setModal(True)
        
        layout = QVBoxLayout()
        
        # Form fields
        form_layout = QFormLayout()
        
        self.edit_title = QLineEdit(task[1])
        self.edit_description = QTextEdit(task[2])
        self.edit_due_date = QDateEdit(QDate.fromString(task[3], "yyyy-MM-dd"))
        self.edit_due_time = QTimeEdit(QTime.fromString(task[4], "hh:mm"))
        
        self.edit_priority = QComboBox()
        self.edit_priority.addItems(["High", "Medium", "Low"])
        self.edit_priority.setCurrentText(task[5])
        
        self.edit_status = QComboBox()
        self.edit_status.addItems(["Pending", "Completed"])
        self.edit_status.setCurrentText(task[6])
        
        self.edit_category = QLineEdit(task[7])
        self.edit_recurrence = QComboBox()
        self.edit_recurrence.addItems(["None", "Daily", "Weekly", "Monthly"])
        if task[8]:
            self.edit_recurrence.setCurrentText(task[8])
        
        self.edit_attachment = QLineEdit(task[9] if task[9] else "")
        self.edit_attachment.setReadOnly(True)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_attachment(self.edit_attachment))
        
        attachment_layout = QHBoxLayout()
        attachment_layout.addWidget(self.edit_attachment)
        attachment_layout.addWidget(browse_btn)
        
        form_layout.addRow("Title:", self.edit_title)
        form_layout.addRow("Description:", self.edit_description)
        form_layout.addRow("Due Date:", self.edit_due_date)
        form_layout.addRow("Due Time:", self.edit_due_time)
        form_layout.addRow("Priority:", self.edit_priority)
        form_layout.addRow("Status:", self.edit_status)
        form_layout.addRow("Category:", self.edit_category)
        form_layout.addRow("Recurrence:", self.edit_recurrence)
        form_layout.addRow("Attachment:", attachment_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.update_task(task_id, self.edit_dialog))
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.edit_dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add to dialog
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.edit_dialog.setLayout(layout)
        
        self.edit_dialog.exec_()
    
    def update_task(self, task_id, dialog):
        # Get all field values
        title = self.edit_title.text()
        description = self.edit_description.toPlainText()
        due_date = self.edit_due_date.date().toString("yyyy-MM-dd")
        due_time = self.edit_due_time.time().toString("hh:mm")
        priority = self.edit_priority.currentText()
        status = self.edit_status.currentText()
        category = self.edit_category.text()
        recurrence = self.edit_recurrence.currentText()
        attachment = self.edit_attachment.text()
        
        # Validate
        if not title:
            QMessageBox.warning(self, "Warning", "Title is required!")
            return
        
        # Update database
        query = """
            UPDATE Tasks 
            SET title=?, description=?, due_date=?, due_time=?, priority=?, 
                status=?, category=?, recurrence=?, attachment_path=?
            WHERE id=?
        """
        try:
            self.cursor.execute(query, (title, description, due_date, due_time, priority, 
                                      status, category, recurrence, attachment, task_id))
            self.conn.commit()
            
            # If task was marked as completed, add to history
            if status == "Completed":
                self.cursor.execute("INSERT INTO TaskHistory (task_id, completion_date) VALUES (?, datetime('now'))", 
                                  (task_id,))
                self.conn.commit()
            
            # Refresh UI
            self.load_tasks()
            self.update_dashboard()
            
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update task:\n{str(e)}")
    
    def delete_task(self):
        selected = self.task_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a task to delete!")
            return
        
        task_id = selected[0].text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete task #{task_id}?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete from database
            try:
                self.cursor.execute("DELETE FROM Tasks WHERE id=?", (task_id,))
                self.cursor.execute("DELETE FROM TaskHistory WHERE task_id=?", (task_id,))
                self.conn.commit()
                
                # Refresh UI
                self.load_tasks()
                self.update_dashboard()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete task:\n{str(e)}")
    
    def search_tasks(self):
        search_term = self.search_input.text()
        if not search_term:
            self.load_tasks()
            return
        
        query = """
            SELECT id, title, due_date, priority, status, category 
            FROM Tasks 
            WHERE title LIKE ? OR description LIKE ? OR category LIKE ?
        """
        try:
            self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            tasks = self.cursor.fetchall()
            
            self.task_table.setRowCount(len(tasks))
            for row, task in enumerate(tasks):
                for col, data in enumerate(task):
                    self.task_table.setItem(row, col, QTableWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to search tasks:\n{str(e)}")
    
    def filter_tasks(self):
        filter_text = self.filter_combo.currentText()
        
        if filter_text == "All":
            self.load_tasks()
            return
        
        try:
            if filter_text == "Pending":
                query = "SELECT id, title, due_date, priority, status, category FROM Tasks WHERE status='Pending'"
            elif filter_text == "Completed":
                query = "SELECT id, title, due_date, priority, status, category FROM Tasks WHERE status='Completed'"
            elif filter_text == "High Priority":
                query = "SELECT id, title, due_date, priority, status, category FROM Tasks WHERE priority='High'"
            elif filter_text == "Medium Priority":
                query = "SELECT id, title, due_date, priority, status, category FROM Tasks WHERE priority='Medium'"
            elif filter_text == "Low Priority":
                query = "SELECT id, title, due_date, priority, status, category FROM Tasks WHERE priority='Low'"
            
            self.cursor.execute(query)
            tasks = self.cursor.fetchall()
            
            self.task_table.setRowCount(len(tasks))
            for row, task in enumerate(tasks):
                for col, data in enumerate(task):
                    self.task_table.setItem(row, col, QTableWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to filter tasks:\n{str(e)}")
    
    def backup_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Backup Database", 
            "", 
            "SQLite Database (*.db *.sqlite)"
        )
        
        if file_path:
            try:
                # Simple file copy for backup
                import shutil
                shutil.copy2('task_manager.db', file_path)
                QMessageBox.information(self, "Success", "Database backup created successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create backup:\n{str(e)}")
    
    def restore_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Restore Database", 
            "", 
            "SQLite Database (*.db *.sqlite)"
        )
        
        if file_path:
            try:
                # Simple file copy for restore
                import shutil
                shutil.copy2(file_path, 'task_manager.db')
                QMessageBox.information(self, "Success", "Database restored successfully!")
                
                # Refresh UI
                self.load_tasks()
                self.update_dashboard()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restore backup:\n{str(e)}")
    
    def closeEvent(self, event):
        # Clean up database connection
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartTaskManager()
    window.show()
    sys.exit(app.exec_())