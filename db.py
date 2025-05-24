import datetime
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import Error

load_dotenv()


class DB:

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
                          create table IF NOT EXISTS users
                          (
                              id          SERIAL PRIMARY KEY,
                              username    VARCHAR(128) UNIQUE,
                              telegram_id BIGINT,
                              first_name  VARCHAR(255),
                              roles        VARCHAR(25) DEFAULT 'user'
                          ); """
        cursor.execute(create_user_sql)
        self.db.commit()
        cursor.close()

    def create_client_table(self):
        cursor = self.db.cursor()
        create_client_sql = """
                            CREATE TABLE IF NOT EXISTS clients
                            (
                                id           SERIAL PRIMARY KEY,
                                name         VARCHAR(255) NOT NULL UNIQUE,
                                company      varchar(255) NOT NULL ,
                                created_at   DATE DEFAULT CURRENT_DATE + INTERVAL '1 DAY',
                                end_date     DATE DEFAULT CURRENT_DATE + INTERVAL '1 MONTH',
                                status       VARCHAR(255) NOT NULL DEFAULT 'new',
                                phone_number VARCHAR(20)  NOT NULL UNIQUE,
                                masul_xodim VARCHAR(50) NOT NULL 
                            );"""
        cursor.execute(create_client_sql)
        self.db.commit()
        cursor.close()

    def insert_user(self, username, telegram_id, first_name):
        cursor = self.db.cursor()
        insert_into_users = """
                            INSERT INTO users(username, telegram_id, first_name)
                            VALUES (%s, %s, %s); 
                            """
        cursor.execute(insert_into_users, (username, telegram_id, first_name,))
        self.db.commit()
        cursor.close()

    def insert_client(self, name: str, company, created_at: datetime, end_date: datetime, phone_number: str,masul_xodim):
        cursor = self.db.cursor()
        insert_client_sql = """
                            INSERT INTO clients(name, company, created_at, end_date, phone_number,masul_xodim)
                            VALUES (%s, %s, %s, %s, %s,%s);"""
        cursor.execute(insert_client_sql, (name, company, created_at, end_date, phone_number,masul_xodim))
        self.db.commit()
        cursor.close()


    def check_user_exist(self, telegram_id: int):
        cursor = self.db.cursor()
        data_sql = "SELECT telegram_id FROM users WHERE telegram_id = %s;"
        cursor.execute(data_sql, (telegram_id,))
        data = cursor.fetchone()
        cursor.close()
        return data is not None

    def check_unique_phone_number(self,phone_number):
        cursor = self.db.cursor()
        unique_phone_number_sql = """SELECT phone_number FROM clients WHERE phone_number=%s;"""
        cursor.execute(unique_phone_number_sql,(phone_number,))
        data = cursor.fetchone()
        cursor.close()
        return data is not None


    def check_client_name_unique(self,name):
        cursor = self.db.cursor()
        unique_client_name_sql = """SELECT name FROM clients WHERE name=%s;"""
        cursor.execute(unique_client_name_sql,(name,))
        data = cursor.fetchone()
        cursor.close()
        return data is not None


    def check_phone_number_exists(self,phone_number):
        cursor = self.db.cursor()
        phone_number_exist_sql="""SELECT phone_number FROM clients WHERE phone_number=%s;"""
        cursor.execute(phone_number_exist_sql,(phone_number,))
        data = cursor.fetchone()
        cursor.close()
        return data is not None


    def update_date(self,phone_number,boshlanish_date,tugash_date):
        cursor = self.db.cursor()
        update_date_sql = """ UPDATE clients SET created_at = %s,end_date = %s
        WHERE phone_number = %s;"""
        cursor.execute(update_date_sql, (boshlanish_date, tugash_date, phone_number))
        self.db.commit()
        cursor.close()


    def get_mijoz(self,phone_number):
        cursor = self.db.cursor()
        get_mijoz_sql = """SELECT * FROM clients WHERE phone_number=%s;"""
        cursor.execute(get_mijoz_sql,(phone_number,))
        self.db.commit()
        data = cursor.fetchone()
        cursor.close()
        return data


    def update_admin(self,telegram_id):
        cursor = self.db.cursor()
        update_user_sql="""UPDATE clients SET role ='admin' WHERE telegram_id=%s ;"""
        cursor.execute(update_user_sql,(telegram_id,))
        self.db.commit()
        cursor.close()

if __name__ == '__main__':
    db = DB()
    db.create_user_table()
    db.create_client_table()
