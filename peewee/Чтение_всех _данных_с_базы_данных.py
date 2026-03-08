from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html

db = SqliteDatabase("people.db")


async def read_from_db():
    """Функция для чтения данных из базы данных. Считываем данные из базы данных"""
    db.connect()
    rows = Employee.select()  # Получаем все записи из таблицы employees
    db.close()  # Закрываем подключение к базе данных
    return rows
