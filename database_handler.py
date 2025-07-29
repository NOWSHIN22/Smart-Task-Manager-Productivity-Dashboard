import mysql.connector
from mysql.connector import Error
from datetime import datetime

class DatabaseHandler:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def execute_query(self, query, params=None, fetch=False):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            self.connection.commit()
        except Error as e:
            print(f"MySQL error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    # --- Task Operations ---
    def create_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS Tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date DATE,
                due_time TIME,
                priority ENUM('High', 'Medium', 'Low') NOT NULL,
                status ENUM('Pending', 'Completed') DEFAULT 'Pending',
                category VARCHAR(100),
                recurrence ENUM('None', 'Daily', 'Weekly', 'Monthly') DEFAULT 'None',
                attachment_path TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS TaskHistory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT,
                completion_date DATETIME,
                FOREIGN KEY (task_id) REFERENCES Tasks(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS UserSettings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_name VARCHAR(100) UNIQUE,
                setting_value TEXT
            )
            """
        ]
        for query in queries:
            self.execute_query(query)

    def add_task(self, task_data):
        query = """
            INSERT INTO Tasks 
            (title, description, due_date, due_time, priority, status, category, recurrence, attachment_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.execute_query(query, task_data)
        return self.connection.lastrowid

    def update_task(self, task_id, task_data):
        query = """
            UPDATE Tasks 
            SET title=%s, description=%s, due_date=%s, due_time=%s, priority=%s,
                status=%s, category=%s, recurrence=%s, attachment_path=%s
            WHERE id=%s
        """
        self.execute_query(query, (*task_data, task_id))

    def delete_task(self, task_id):
        self.execute_query("DELETE FROM Tasks WHERE id=%s", (task_id,))

    def get_tasks(self, filter_condition=None):
        base_query = "SELECT id, title, due_date, priority, status, category FROM Tasks"
        if filter_condition:
            base_query += f" WHERE {filter_condition}"
        return self.execute_query(base_query, fetch=True)

    # --- Dashboard Stats ---
    def get_task_stats(self):
        stats = {
            'total_tasks': self.execute_query("SELECT COUNT(*) FROM Tasks", fetch=True)[0][0],
            'completed_tasks': self.execute_query("SELECT COUNT(*) FROM Tasks WHERE status='Completed'", fetch=True)[0][0],
            'priority_distribution': self.execute_query(
                "SELECT priority, COUNT(*) FROM Tasks GROUP BY priority", fetch=True
            ),
            'status_distribution': self.execute_query(
                "SELECT status, COUNT(*) FROM Tasks GROUP BY status", fetch=True
            )
        }
        return stats

    # --- Settings ---
    def save_setting(self, name, value):
        query = """
            INSERT INTO UserSettings (setting_name, setting_value)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE setting_value=%s
        """
        self.execute_query(query, (name, value, value))

    def get_setting(self, name):
        result = self.execute_query(
            "SELECT setting_value FROM UserSettings WHERE setting_name=%s",
            (name,), fetch=True
        )
        return result[0][0] if result else None