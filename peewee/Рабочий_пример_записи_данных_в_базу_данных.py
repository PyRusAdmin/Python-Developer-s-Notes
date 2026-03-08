from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html

# Настраиваем синхронную базу данных SQLite
db = SqliteDatabase(f"src/core/database/{DB_NAME}")


class Person(Model):
    """
    Хранит информацию о пользователях, запустивших Telegram-бота вызвав команду /start.
    """

    id_user = IntegerField(unique=True)  # Telegram ID пользователя Telegram (unique=True - уникальный ID)
    first_name = CharField(null=True)  # Telegram Имя пользователя
    last_name = CharField(null=True)  # Telegram Фамилия пользователя
    username = CharField(null=True)  # Telegram username
    lang = CharField(null=True)  # Язык пользователя
    created_at = DateTimeField()  # Время запуска

    class Meta:  # Подключение к базе данных
        database = db  # Модель базы данных
        table_name = "registered_users"  # Имя таблицы


def register_user(user_data) -> None:
    """
    Записывает данные пользователя в базу данных, который вызвал команду /start.

    :param user_data: Словарь с данными пользователя, для последующей записи в БД src/core/database/database.db
    """
    db.connect()  # Подсоединяемся к базе данных
    db.create_tables([Person])  # Создаем таблицу, если она не существует
    person = Person(
        id_user=user_data["id"],  # Telegram ID пользователя Telegram
        first_name=user_data["first_name"],  # Telegram Имя пользователя
        last_name=user_data["last_name"],  # Telegram Фамилия пользователя
        username=user_data["username"],  # Telegram username
        lang=user_data["lang"],  # Язык пользователя
        created_at=user_data["date"],  # Время запуска
    )  # Создаем объект Person с данными пользователя
    person.save()  # Сохраняем данные в базу данных


# Формируем данные пользователя
user_data = {
    "id": message.from_user.id,  # ID пользователя
    "first_name": message.from_user.first_name,  # Имя пользователя
    "last_name": message.from_user.last_name,  # Фамилия пользователя
    "username": message.from_user.username,  # Username пользователя
    "lang": 'ru',  # Язык пользователя (Сделать проверку на наличие в базе данных)
    "date": message.date,  # Дата и время регистрации
}
# Записываем данные пользователя в базу данных src/core/database/database.db
register_user(user_data)
