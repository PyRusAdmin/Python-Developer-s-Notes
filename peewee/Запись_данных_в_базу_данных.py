# https://docs.peewee-orm.com/en/latest/index.html
from datetime import date

from peewee import *

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

# Запись данных в таблицу Person
uncle_bob = Person(name="Иван", birthday=date(1992, 12, 13))
uncle_bob.save()  # Сохраняем в базу данных.

db.close()