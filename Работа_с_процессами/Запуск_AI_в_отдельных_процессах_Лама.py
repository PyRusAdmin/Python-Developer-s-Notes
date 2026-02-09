# -*- coding: utf-8 -*-
import os
import sys
from multiprocessing import Process

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

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
    api_key = os.getenv("POLZA_AI_API_KEY")

    if not api_key:
        raise ValueError("api_key_yandex не найден в .env")

    client = OpenAI(
        base_url="https://api.polza.ai/api/v1",
        api_key=api_key,
    )

    completion = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[
            {
                "role": "user",
                "content": "Что думаешь об этой жизни?"
            }
        ]
    )

    print(f"\n{'=' * 70}")
    print(f"✅ PID {os.getpid()}: {completion.choices[0].message.content}")
    print(f"{'=' * 70}\n")


def main():
    load_env()

    print("\n🚀 Запуск 4 процессов Yandex Assistant...\n")

    processes = []
    for i in range(10):
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