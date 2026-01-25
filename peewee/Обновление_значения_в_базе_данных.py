# https://docs.peewee-orm.com/en/latest/index.html
from datetime import date  # Импортируем date

from peewee import *  # Импортируем peewee

db = SqliteDatabase("people.db")  # Создаем базу данных "people.db"


class Person(Model):  # Создаем модель Person
    name = CharField()  # Имя колонки
    birthday = DateField()  # Имя колонки

    class Meta:  # Метакласс
        database = db  # Эта модель использует базу данных "people.db".


class Pet(Model):  # Создаем модель Pet
    name = CharField()  # Имя колонки
    birthday = DateField()  # Имя колонки

    class Meta:  # Метакласс
        database = db  # Эта модель использует базу данных "people.db".


db.connect()  # Подключаемся к базе данных.
db.create_tables([Person, Pet])  # Создаем таблицы, если их еще нет.

grandma = Person.create(
    name="Grandma", birthday=date(1935, 3, 1)
)  # Создаем запись в таблице Person
grandma.name = "Grandma L."  # Изменяем значение в базе данных.
grandma.save()  # Сохраняем изменения в базе данных.

db.close()