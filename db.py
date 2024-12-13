import mysql.connector

class DatabaseHandler:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=root,
            password=123,
            database=database
        )
        self.cursor = self.connection.cursor()

    def create_table(self):
        """Создание таблицы для хранения данных."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS films (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                spans TEXT,
                times TEXT
            )
        ''')
        self.connection.commit()

    def insert_film(self, title, spans, times):
        """Добавление фильма в таблицу."""
        query = "INSERT INTO films (title, spans, times) VALUES (%s, %s, %s)"
        values = (title, spans, times)
        self.cursor.execute(query, values)
        self.connection.commit()

    def close(self):
        """Закрытие соединения с базой данных."""
        self.cursor.close()
        self.connection.close()
