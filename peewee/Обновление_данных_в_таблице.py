"""Запись в базу данных пользователей, запустивших бота вызвав команду /start."""


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


"""Установка языка пользователя"""

def set_user_lang(id_user: int, lang: str):
    """Обновляет язык пользователя по Telegram ID"""
    with db:
        query = Person.update({Person.lang: lang}).where(Person.id_user == id_user)
        query.execute()