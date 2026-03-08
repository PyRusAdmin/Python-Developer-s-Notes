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

# Получить всех людей, отсортированных по имени
for person in Person.select().order_by(Person.name):
    print(person.name, person.birthday)

# Отсортировать по имени в обратном порядке (Z -> A)
for person in Person.select().order_by(Person.name.desc()):
    print(person.name, person.birthday)

# Или так:
for person in Person.select().order_by(-Person.name):
    print(person.name, person.birthday)

db.close()  # Закрываем базу данных.
