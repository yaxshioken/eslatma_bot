import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


class DB():


    def __init__(self):
        self.db = psycopg2.connect(
            dbname=,
            user=
            password=,
            host=
        )
        self.db.autocommit = True

    # def create_user(self):
    #     cursor = self.db.cursor()
    #     create_user_sql = """
    #     create table  user(
    #     id serial primary key,
    #     first_name varchar(50) not null,
    #     last_name varchar(50),
    #     username varchar(50) unique not null,
    #     email varchar(50) not null,
    #     password varchar(50) not null,
    #     phone varchar(50) not null
    #     );"""
    #     cursor.execute(create_user_sql)
    #     self.db.commit()
    def create_user_table(self):
        cursor = self.db.cursor()
        create_user_sql = """
               create table users(
                   id serial primary key,
                   username varchar(128) unique not null, 
                   password varchar(128) not null,
                   email varchar(56),
                   phone varchar(56)
               );             
           """
        cursor.execute(create_user_sql)
        self.db.commit()

    def create_todo(self):
        cursor = self.db.cursor()
        create_todo_sql = """
        CREATE TABLE   todo(
        id serial PRIMARY KEY,
        title varchar(255) not null ,
        owner_id int  references users(id),
        created_at timestamp default CURRENT_TIMESTAMP+ interval'1 day',
        status varchar(255) not null default 'new'
        );"""
        cursor.execute(create_todo_sql)
        self.db.commit()
    def insert_user(self, username,password, email, phone):
        cursor = self.db.cursor()
        insert_into_users="""
        insert into  users(username, password, email, phone) values (%s, %s, %s, %s);
        """
        cursor.execute(insert_into_users,(username,password,email,phone))
        self.db.commit()


    def insert_todo(self, title, owner_id, created_at, status):
        cursor = self.db.cursor()
        insert_into_todo="""
        insert into todo(title, owner_id, created_at, status) values (%s, %s, %s, %s);
        """
        cursor.execute(insert_into_todo,(title, owner_id, created_at, status))
        self.db.commit()


if __name__ == '__main__':
    db = DB()