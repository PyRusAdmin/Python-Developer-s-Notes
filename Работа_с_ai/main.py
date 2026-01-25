# -*- coding: utf-8 -*-
import os
import base64
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


def save_base64_image(base64_string, filename="generated_image.png"):
    """Сохраняет base64 изображение в файл."""
    # Убираем префикс data:image/png;base64,
    if "base64," in base64_string:
        base64_string = base64_string.split("base64,")[1]

    image_data = base64.b64decode(base64_string)

    with open(filename, "wb") as f:
        f.write(image_data)

    logger.info(f"Изображение сохранено: {filename}")
    return filename


def generate_image(prompt, model="google/gemini-2.5-flash-image"):
    """Генерирует изображение по текстовому промпту."""
    load_env()
    proxies = setup_proxy()

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        logger.error("OPENROUTER_API_KEY не найден в .env файле!")
        raise ValueError("OPENROUTER_API_KEY is required in .env file")

    logger.info(f"Генерация изображения: {prompt}")

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "modalities": ["image", "text"]
        }),
        proxies=proxies
    )

    if response.status_code != 200:
        logger.error(f"Ошибка API: {response.status_code} - {response.text}")
        raise Exception(f"API error: {response.status_code}")

    result = response.json()

    # Проверяем наличие изображений в ответе
    if result.get("choices"):
        message = result["choices"][0]["message"]

        # Если есть текстовый ответ
        if message.get("content"):
            logger.info(f"Текстовый ответ: {message['content']}")

        # Если есть изображения
        if message.get("images"):
            images = []
            for idx, image in enumerate(message["images"]):
                image_url = image["image_url"]["url"]
                filename = f"generated_image_{idx + 1}.png"
                saved_file = save_base64_image(image_url, filename)
                images.append(saved_file)
                logger.success(f"Изображение {idx + 1} сохранено: {saved_file}")

            return images
        else:
            logger.warning("Изображения не сгенерированы")
            return None
    else:
        logger.error("Некорректный ответ от API")
        return None


def main():
    # Ваш промпт для генерации изображения
    prompt = "Сгенерируй девушку лет 20 в красном платье и в парке. "

    try:
        images = generate_image(prompt)

        if images:
            print(f"\n✅ Успешно сгенерировано изображений: {len(images)}")
            for img in images:
                print(f"   📁 {img}")
        else:
            print("\n❌ Изображения не были сгенерированы")

    except Exception as e:
        logger.exception("Произошла ошибка")
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    main()