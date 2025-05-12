import datetime
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DB():

    def __init__(self):
        self.db = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.db.autocommit = True

    def create_user_table(self):
        cursor = self.db.cursor()
        create_user_sql = """
                          create table users
                          (
                              id          serial primary key,
                              username    varchar(128) unique,
                              telegram_id bigint,
                              first_name  varchar(255),
                              role        varchar(25) default 'user',
                              phone       varchar(14)
                          ); """
        cursor.execute(create_user_sql)
        self.db.commit()

    def create_client_table(self):
        cursor = self.db.cursor()
        create_client_sql = """
                            CREATE TABLE todo
                            (
                                id         SERIAL PRIMARY KEY,
                                name       VARCHAR(255) NOT NULL,
                                created_at TIMESTAMP             DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 hour',
                                end_date   TIMESTAMP,
                                status     VARCHAR(255) NOT NULL DEFAULT 'new'
                            );"""
        cursor.execute(create_client_sql)
        self.db.commit()

    def insert_user(self, username: str, telegram_id: int, first_name, phone):
        cursor = self.db.cursor()
        insert_into_users = """
                            insert into users(username, telegram_id, first_name, phone)
                            values (%s, %s, %s, %s); \
                            """
        cursor.execute(insert_into_users, (username, telegram_id, first_name, phone))
        self.db.commit()

    def insert_client(self, name: str, created_at: datetime, end_date: datetime, phone_number: str):
        cursor = self.db.cursor()
        insert_client_sql = """
                            insert into todo(name, created_at, end_date)
                            values (%s, %s, %s, %s);"""
        cursor.execute(insert_client_sql, (name, created_at, end_date, phone_number))
        self.db.commit()

    def check_client_exist(self, user_id: int):
        cursor = self.db.cursor()
        data_sql = "SELECT telegram_id FROM users WHERE telegram_id = %s"

        cursor.execute(data_sql, (user_id,))  # Tuple format to avoid the TypeError

        data = cursor.fetchone()
        if data:
            return True
        else:
            return False


if __name__ == '__main__':
    db = DB()
