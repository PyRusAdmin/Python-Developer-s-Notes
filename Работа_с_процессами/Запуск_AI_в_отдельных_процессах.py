# -*- coding: utf-8 -*-
import os
import sys
import time
from multiprocessing import Process

from dotenv import load_dotenv
from openai import OpenAI
from loguru import logger

# Отключаем стандартный логгер для чистого вывода в мультипроцессинге
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

def load_env():
    """Загружает переменные окружения из .env."""
    dotenv_path = '.env'
    if not os.path.exists(dotenv_path):
        logger.error(f"Файл .env не найден: {dotenv_path}")
        raise FileNotFoundError(f".env file not found at {dotenv_path}")

    load_dotenv(dotenv_path)
    logger.info("✅ Переменные окружения загружены")

def setup_yandex_client():
    """Инициализирует клиент YandexGPT через OpenAI-совместимый API."""
    api_key = os.getenv("YANDEX_API_KEY")
    folder_id = os.getenv("YANDEX_FOLDER_ID")

    if not api_key:
        raise ValueError("YANDEX_API_KEY не найден в .env")
    if not folder_id:
        raise ValueError("YANDEX_FOLDER_ID не найден в .env")

    # Правильный базовый URL для YandexGPT (без пробелов!)
    return OpenAI(
        api_key=api_key,
        base_url="https://api.llm.yandex.net/v1",  # Официальный endpoint
        default_headers={"x-folder-id": folder_id}  # Критически важно для аутентификации
    )

def ai_worker(model_name: str, prompt: str, reserve_ram_mb: int, worker_id: int):
    """
    Процесс: резервирует RAM + делает запрос к модели YandexGPT.

    Args:
        model_name: Название модели (например, "yandexgpt/latest")
        prompt: Промпт для модели
        reserve_ram_mb: Сколько МБ локальной RAM зарезервировать
        worker_id: ID воркера для логирования
    """
    pid = os.getpid()
    logger.info(f"[Worker-{worker_id}] PID {pid} | Модель: {model_name} | Резервирую {reserve_ram_mb} МБ RAM...")

    # === 1. ЛОКАЛЬНОЕ РЕЗЕРВИРОВАНИЕ RAM (без нагрузки на CPU) ===
    if reserve_ram_mb > 0:
        ram_buffer = bytearray(reserve_ram_mb * 1024 * 1024)
        # Заполняем память чтобы ОС реально выделила физическую RAM
        for i in range(0, len(ram_buffer), 1024 * 1024):
            ram_buffer[i:i + 1024 * 1024] = b'X' * min(1024 * 1024, len(ram_buffer) - i)
        logger.info(f"[Worker-{worker_id}] PID {pid} | ✅ {reserve_ram_mb} МБ RAM зарезервировано")

    # === 2. ЗАПРОС К YANDEXGPT ===
    try:
        client = setup_yandex_client()
        logger.info(f"[Worker-{worker_id}] PID {pid} | Отправляю запрос к '{model_name}'...")

        # Важно: для Яндекса используется стандартный chat.completions.create
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=256,
            stream=False
        )

        result = completion.choices[0].message.content.strip()

        # Выводим результат с разделителем для читаемости
        print(f"\n{'=' * 70}")
        print(f"✅ [Worker-{worker_id}] Модель: {model_name}")
        print(f"   Промпт: «{prompt[:40]}...»")
        print(f"   PID: {pid} | RAM: {reserve_ram_mb} МБ")
        print(f"{'=' * 70}")
        print(result)
        print(f"{'=' * 70}\n")

    except Exception as e:
        logger.error(f"[Worker-{worker_id}] PID {pid} | Ошибка YandexGPT ({model_name}): {e}")
        logger.error(f"[Worker-{worker_id}] PID {pid} | Детали: {str(e)}")

    # === 3. УДЕРЖИВАЕМ ПАМЯТЬ БЕЗ НАГРУЗКИ НА CPU ===
    if reserve_ram_mb > 0:
        logger.info(f"[Worker-{worker_id}] PID {pid} | Удерживаю {reserve_ram_mb} МБ RAM (Ctrl+C для завершения)...")
        while True:
            time.sleep(60)

def main():
    load_env()

    # Конфигурация: 4 разных модели/конфигурации YandexGPT
    models_config = [
        {
            "name": "aliceai-llm/latest",
            "prompt": "Напиши короткий анекдот про программистов и кофе",
            "ram_mb": 300
        },
        {
            "name": "aliceai-llm/latest",
            "prompt": "Объясни квантовую запутанность простыми словами за 3 предложения",
            "ram_mb": 300
        },
        {
            "name": "aliceai-llm/latest",
            "prompt": "Придумай 3 необычных идеи для стартапа в сфере AI",
            "ram_mb": 300
        },
        {
            "name": "aliceai-llm/latest",  # Повторяем основную модель с другим промптом
            "prompt": "Напиши рецепт идеального утреннего кофе в 4 шага",
            "ram_mb": 300
        }
    ]

    processes = []

    print("\n🚀 Запуск 4 процессов с разными моделями YandexGPT + резервированием RAM...\n")

    for i, cfg in enumerate(models_config):
        p = Process(
            target=ai_worker,
            args=(cfg["name"], cfg["prompt"], cfg["ram_mb"], i),
            name=f"YandexWorker-{i}"
        )
        p.start()
        processes.append(p)
        logger.info(f"Запущен [Worker-{i}] | Модель: {cfg['name']} | RAM: {cfg['ram_mb']} МБ | PID: {p.pid}")
        time.sleep(1.5)  # Задержка для избежания ограничений API

    total_ram = sum(cfg["ram_mb"] for cfg in models_config)
    print(f"\n✅ Все процессы запущены. Всего зарезервировано: ~{total_ram} МБ RAM")
    print("💡 Совет: Откройте диспетчер задач (Ctrl+Shift+Esc) чтобы увидеть потребление памяти\n")

    # Удерживаем основной процесс живым
    try:
        while any(p.is_alive() for p in processes):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал завершения. Останавливаем процессы...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join(timeout=3)
        print("✅ Все процессы остановлены. Память освобождена.")

if __name__ == '__main__':
    # Защита для Windows
    if sys.platform.startswith('win'):
        import multiprocessing
        multiprocessing.freeze_support()

    main()