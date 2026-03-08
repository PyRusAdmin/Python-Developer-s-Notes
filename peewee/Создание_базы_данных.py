from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html

db = SqliteDatabase("people.db")


class Person(Model):
    name = CharField()  # Имя колонки
    birthday = DateField()  # Имя колонки

    class Meta:
        database = db  # Эта модель использует базу данных "people.db".


class Pet(Model):
    name = CharField()  # Имя колонки
    birthday = DateField()  # Имя колонки

    class Meta:
        database = db  # Эта модель использует базу данных "people.db".


db.connect()  # Подключаемся к базе данных.
db.create_tables([Person, Pet])  # Создаем таблицы, если их еще нет.

db.close()
