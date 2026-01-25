

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


"""Получение языка пользователя"""


def get_user_lang(id_user: int) -> str | None:
    """Возвращает язык пользователя по Telegram ID. Если пользователь не найден — None."""
    with db:
        user = Person.get_or_none(Person.id_user == id_user)
        return user.lang if user else None
