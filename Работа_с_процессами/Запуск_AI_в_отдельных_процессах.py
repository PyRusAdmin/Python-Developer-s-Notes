# -*- coding: utf-8 -*-
import os
import sys
from multiprocessing import Process

import openai
from dotenv import load_dotenv
from loguru import logger

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")


def load_env():
    """Загружает переменные окружения из .env."""
    if not os.path.exists('.env'):
        logger.error("Файл .env не найден")
        raise FileNotFoundError(".env file not found")

    load_dotenv('.env')
    logger.info("✅ Переменные окружения загружены")


def ai_yandex():
    """Запрос к Yandex Assistant API."""
    api_key = os.getenv("api_key_yandex")

    if not api_key:
        raise ValueError("api_key_yandex не найден в .env")

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project="b1g91an2voo0a348k3t3"
    )

    response = client.responses.create(
        prompt={"id": "fvt7llvjnet8ca158tp6"},
        input="Сколько потоков ты можешь запустить?",
    )

    print(f"\n{'=' * 70}")
    print(f"✅ PID {os.getpid()}: {response.output_text}")
    print(f"{'=' * 70}\n")


def main():
    load_env()

    print("\n🚀 Запуск 4 процессов Yandex Assistant...\n")

    processes = []
    for i in range(4):
        p = Process(target=ai_yandex, name=f"YandexAgent-{i}")
        p.start()
        processes.append(p)
        logger.info(f"Запущен Agent-{i} | PID: {p.pid}")

    # Ожидаем завершения всех процессов
    for p in processes:
        p.join()

    print("\n✅ Все процессы завершены")


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        import multiprocessing
        multiprocessing.freeze_support()

    main()