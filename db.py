import datetime
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import Error

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
                              telegram_id BIGINT,
                              first_name  varchar(255),
                              role        varchar(25) default 'user'
                          ); """
        cursor.execute(create_user_sql)
        self.db.commit()

    def create_client_table(self):
        cursor = self.db.cursor()
        create_client_sql = """
                            CREATE TABLE client
                            (
                                id           SERIAL PRIMARY KEY,
                                name         VARCHAR(255) NOT NULL unique,
                                company      varchar(255) not null unique,
                                created_at   DATE                  DEFAULT CURRENT_DATE + INTERVAL '1 DAY',
                                end_date     date                  DEFAULT CURRENT_DATE + INTERVAL '1 MONTH',
                                status       VARCHAR(255) NOT NULL DEFAULT 'new',
                                phone_number VARCHAR(20)  NOT NULL unique
                            );"""
        cursor.execute(create_client_sql)
        self.db.commit()

    def insert_user(self, username, telegram_id, first_name):
        cursor = self.db.cursor()
        insert_into_users = """
                            insert into users(username, telegram_id, first_name)
                            values (%s, %s, %s); \
                            """
        cursor.execute(insert_into_users, (username, telegram_id, first_name,))
        self.db.commit()

    def insert_client(self, name: str, company, created_at: datetime, end_date: datetime, phone_number: str):
        cursor = self.db.cursor()
        insert_client_sql = """
                            insert into client(name, company, created_at, end_date, phone_number)
                            values (%s, %s, %s, %s, %s);"""
        try:
            cursor.execute(insert_client_sql, (name, company, created_at, end_date, phone_number))
        except Error as e:
            return e
        if not self.db.commit():
            return True
        else:
            return False

        print(self.db.commit())

    def check_user_exist(self, user_id: int):
        cursor = self.db.cursor()
        data_sql = "SELECT telegram_id FROM users WHERE telegram_id = %s"
        cursor.execute(data_sql, (user_id,))
        data = cursor.fetchone()
        return data is not None


if __name__ == '__main__':
    db = DB()
    db.create_user_table()
    db.create_client_table()
