# -*- coding: utf-8 -*-
import os

import openai
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


load_env()

api_key = os.getenv("api_key_yandex")

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project="b1g91an2voo0a348k3t3"
)

response = client.responses.create(
    prompt={
        "id": "fvt7llvjnet8ca158tp6",
    },
    input="Сколько потоков ты можешь запустить?",
)

print(response.output_text)
