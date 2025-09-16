# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

user = os.getenv("USER")  # Пользователь для прокси
password = os.getenv("PASSWORD")  # Пароль для прокси
port = os.getenv("PORT")  # Порт для прокси
ip = os.getenv("IP")  # IP адрес прокси


def setup_proxy():
    # Указываем прокси для HTTP и HTTPS
    os.environ['http_proxy'] = f"http://{user}:{password}@{ip}:{port}"
    os.environ['https_proxy'] = f"http://{user}:{password}@{ip}:{port}"


if __name__ == '__main__':
    setup_proxy()
