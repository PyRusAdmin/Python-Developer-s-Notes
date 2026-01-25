# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from loguru import logger
import requests
import json


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


def get_embeddings(text, model="qwen/qwen3-embedding-8b"):
    """
    Получает векторное представление (embeddings) для текста.

    Args:
        text: Строка текста или список строк для получения embeddings
        model: Модель для генерации embeddings

    Returns:
        list: Список векторов (embeddings) для каждого текста
    """
    load_env()
    proxies = setup_proxy()

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        logger.error("OPENROUTER_API_KEY не найден в .env файле!")
        raise ValueError("OPENROUTER_API_KEY is required in .env file")

    logger.info(f"Получение embeddings для текста: {text if isinstance(text, str) else f'{len(text)} текстов'}")

    response = requests.post(
        url="https://openrouter.ai/api/v1/embeddings",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": model,
            "input": text,
            "encoding_format": "float"
        }),
        proxies=proxies
    )

    if response.status_code != 200:
        logger.error(f"Ошибка API: {response.status_code} - {response.text}")
        raise Exception(f"API error: {response.status_code}")

    result = response.json()

    # Извлекаем embeddings из ответа
    if result.get("data"):
        embeddings = [item["embedding"] for item in result["data"]]
        logger.success(f"Получено {len(embeddings)} embedding(s)")
        return embeddings
    else:
        logger.error("Некорректный ответ от API")
        return None


def main():
    # Пример 1: Один текст
    text = "Это пример текста для получения векторного представления"

    try:
        embeddings = get_embeddings(text)

        if embeddings:
            print(f"\n✅ Получен embedding для текста")
            print(f"   Размерность вектора: {len(embeddings[0])}")
            print(f"   Первые 5 значений: {embeddings[0][:5]}")
        else:
            print("\n❌ Embeddings не были получены")

    except Exception as e:
        logger.exception("Произошла ошибка")
        print(f"\n❌ Ошибка: {e}")

    print("\n" + "="*50 + "\n")

    # Пример 2: Несколько текстов (batch)
    texts = [
        "Первый текст для анализа",
        "Второй текст для сравнения",
        "Третий текст в наборе"
    ]

    try:
        embeddings = get_embeddings(texts)

        if embeddings:
            print(f"\n✅ Получено {len(embeddings)} embeddings")
            for idx, emb in enumerate(embeddings):
                print(f"   Текст {idx + 1}: размерность = {len(emb)}, первые 3 значения = {emb[:3]}")
        else:
            print("\n❌ Embeddings не были получены")

    except Exception as e:
        logger.exception("Произошла ошибка")
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    main()