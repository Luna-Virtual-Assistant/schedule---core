import psycopg2
from psycopg2 import Error


class DatabaseHandler:
    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
            self.cursor = self.connection.cursor()
        except (Exception, Error) as error:
            raise error

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def select_all_from_table(self, table_name):
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            records = self.cursor.fetchall()
            return records
        except (Exception, Error) as error:
            raise error

    def select_schedules_by_date(self, table_name):
        try:
            self.cursor.execute(
                f"SELECT * FROM {table_name} WHERE schedule_date > CURRENT_TIMESTAMP")
            records = self.cursor.fetchall()
            return records
        except (Exception, Error) as error:
            raise error
        
    def select_schedule_by_id(self, schedule_id: int, table_name="schedules"):
        try:
            self.cursor.execute(f"SELECT * FROM {table_name} WHERE id = {schedule_id}")
            record = self.cursor.fetchone()
            return record
        except (Exception, Error) as error:
            raise error

    def update_row(self, table_name, updates, condition_column, condition_value):
        try:
            set_clause = ", ".join([f"{column} = %s" for column in updates.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_column} = %s"
            self.cursor.execute(query, list(updates.values()) + [condition_value])
            self.connection.commit()
        except (Exception, Error) as error:
            raise error

    def delete_row(self, table_name, condition_column, condition_value):
        try:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition_column} = %s", (condition_value,))
            self.connection.commit()

        except (Exception, Error) as error:
            raise error

    def insert_row(self, table_name, values):
        try:
            self.cursor.execute("SET TIMEZONE TO 'UTC';")
            self.cursor.execute(
                f"INSERT INTO {table_name} (text, schedule_date, sessionName) VALUES (%s, %s, %s) RETURNING id", values)
            inserted_row = self.cursor.fetchone()[0]
            self.connection.commit()
            return inserted_row
        except (Exception, Error) as error:
            raise error
        
    def create_table(self):
        try:
            self.connect()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    id serial primary key,
                    text varchar(200),
                    schedule_date timestamp with time zone default CURRENT_TIMESTAMP,
                    sessionname varchar(20))
                """)
            self.connection.commit()
            self.disconnect()
        except (Exception, Error) as error:
            raise error