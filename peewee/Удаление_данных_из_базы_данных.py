from peewee import *  # Импортируем peewee # https://docs.peewee-orm.com/en/latest/index.html

db = SqliteDatabase("people.db")  # Создаем базу данных "people.db"


class Pet(Model):  # Создаем модель Pet
    name = CharField()  # Имя колонки
    birthday = DateField()  # Имя колонки

    class Meta:  # Метакласс
        database = db  # Эта модель использует базу данных "people.db".


db.connect()  # Подключаемся к базе данных.
herb_mittens = Pet.get(name="Fido")
herb_mittens.delete_instance()  # Удаляем запись из таблицы Pet
db.close()
