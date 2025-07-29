import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QDate, QTime
from database_handler import DatabaseHandler

class SmartTaskManager:
    def __init__(self):
        # Initialize MySQL connection
        self.db = DatabaseHandler(
            host="localhost",
            user="your_username",
            password="your_password",
            database="task_manager"
        )
        self.db.create_tables()

    # --- Task Management ---
    def add_task(self, title, description, due_date, due_time, priority, 
                status, category, recurrence, attachment_path):
        task_data = (
            title, description, due_date.toString("yyyy-MM-dd"),
            due_time.toString("hh:mm:ss"), priority, status, 
            category, recurrence, attachment_path
        )
        task_id = self.db.add_task(task_data)
        if status == "Completed":
            self.db.execute_query(
                "INSERT INTO TaskHistory (task_id, completion_date) VALUES (%s, NOW())",
                (task_id,)
            )
        return task_id

    def edit_task(self, task_id, **updates):
        if 'due_date' in updates:
            updates['due_date'] = updates['due_date'].toString("yyyy-MM-dd")
        if 'due_time' in updates:
            updates['due_time'] = updates['due_time'].toString("hh:mm:ss")
        
        set_clause = ", ".join([f"{k}=%s" for k in updates.keys()])
        query = f"UPDATE Tasks SET {set_clause} WHERE id=%s"
        self.db.execute_query(query, (*updates.values(), task_id))

    def delete_task(self, task_id):
        self.db.delete_task(task_id)

    def search_tasks(self, search_term):
        query = """
            SELECT id, title, due_date, priority, status, category 
            FROM Tasks 
            WHERE title LIKE %s OR description LIKE %s OR category LIKE %s
        """
        return self.db.execute_query(
            query, 
            (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"), 
            fetch=True
        )

    # --- Dashboard ---
    def get_productivity_stats(self):
        stats = self.db.get_task_stats()
        
        completion_percentage = 0
        if stats['total_tasks'] > 0:
            completion_percentage = (stats['completed_tasks'] / stats['total_tasks']) * 100
        
        return {
            'total_tasks': stats['total_tasks'],
            'completed_tasks': stats['completed_tasks'],
            'completion_percentage': completion_percentage,
            'priority_data': dict(stats['priority_distribution']),
            'status_data': dict(stats['status_distribution'])
        }

    # --- Settings ---
    def update_pomodoro_settings(self, work_duration, break_duration):
        self.db.save_setting("pomodoro_work", str(work_duration))
        self.db.save_setting("pomodoro_break", str(break_duration))

    def get_pomodoro_settings(self):
        return {
            'work': int(self.db.get_setting("pomodoro_work") or 25),
            'break': int(self.db.get_setting("pomodoro_break") or 5)
        }

    # --- Utility ---
    def close(self):
        self.db.disconnect()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = SmartTaskManager()
    
    # Example usage:
    task_id = manager.add_task(
        title="Finish project",
        description="Complete all pending tasks",
        due_date=QDate.currentDate(),
        due_time=QTime.currentTime(),
        priority="High",
        status="Pending",
        category="Work",
        recurrence="None",
        attachment_path=""
    )
    
    print(f"Added task with ID: {task_id}")
    manager.close()
    sys.exit(app.exec_())