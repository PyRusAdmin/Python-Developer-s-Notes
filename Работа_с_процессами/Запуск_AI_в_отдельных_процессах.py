# -*- coding: utf-8 -*-
import os
import time
from multiprocessing import Process

from dotenv import load_dotenv
from loguru import logger


def load_env():
    """Загружает переменные окружения из файла .env."""
    dotenv_path = '.env'
    if not os.path.exists(dotenv_path):
        logger.error(f"Файл .env не найден по пути: {dotenv_path}")
        raise FileNotFoundError(f".env file not found at {dotenv_path}")

    load_dotenv(dotenv_path)
    logger.info("Переменные окружения загружены из .env")


def setup_proxy():
    """Настраивает прокси, используя переменные окружения из .env."""
    try:
        proxy_user = os.getenv("PROXY_USER")
        proxy_password = os.getenv("PROXY_PASSWORD")
        proxy_ip = os.getenv("PROXY_IP")
        proxy_port = os.getenv("PROXY_PORT")

        if not all([proxy_user, proxy_password, proxy_ip, proxy_port]):
            missing = [k for k, v in {
                "PROXY_USER": proxy_user,
                "PROXY_PASSWORD": proxy_password,
                "PROXY_IP": proxy_ip,
                "PROXY_PORT": proxy_port
            }.items() if not v]
            raise ValueError(f"Отсутствуют обязательные переменные в .env: {missing}")

        proxy_url = f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}"

        logger.info("Прокси успешно настроено")
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    except Exception as e:
        logger.exception("Ошибка при настройке прокси")
        raise


def eat_ram(mb: int):
    """Потребляет указанное количество МБ памяти без нагрузки на CPU"""
    data = bytearray(mb * 1024 * 1024)  # Выделение памяти
    print(f"PID {os.getpid()}: выделено {mb} МБ RAM")
    time.sleep(3600)  # Удерживаем память 1 час (без нагрузки на CPU)


def main():
    processes = []
    mb_per_process = 50  # МБ на процесс
    number_processes = 10  # Количество процессов

    # Запускаем 4 процесса → ~2 ГБ RAM
    for i in range(number_processes):
        p = Process(target=eat_ram, args=(mb_per_process,))
        p.start()
        processes.append(p)

    # Не вызываем join() — процессы работают в фоне
    print(f"\nЗапущено {len(processes)} процессов, удерживающих память...")
    print("Нажмите Ctrl+C для завершения")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nЗавершаем процессы...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()


if __name__ == '__main__':
    main()
