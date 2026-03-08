from peewee import *  # Импортируем peewee # https://docs.peewee-orm.com/en/latest/index.html

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

"""Одиночное чтение из базы данных"""

grandma = Person.select().where(Person.name == "Grandma L.").get()
print(grandma.birthday)  # Выводим дату рождения Грандми.

# Сокращенный синтаксис
grandma = Person.get(Person.name == "Grandma L.")
print(grandma.birthday)  # Выводим дату рождения Грандми.

"""Множественное чтение из базы данных"""
for person in Person.select():
    print(person.name, person.birthday)  # Выводим имя и дату рождения всех людей.

db.close()
