# -*- coding: utf-8 -*-
import base64
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")


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
            logger.warning(f"Пропущены переменные прокси в .env: {missing}. Прокси не будет использован.")
            return None

        proxy_url = f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}"
        logger.info("Прокси успешно настроен")
        return {"http": proxy_url, "https": proxy_url}
    except Exception as e:
        logger.exception("Ошибка при настройке прокси")
        return None


def save_base64_image(base64_string: str, output_path: str):
    """Сохраняет base64-строку как изображение в файл."""
    try:
        # Удаляем префикс data:image/png;base64, если он есть
        if "," in base64_string:
            base64_string = base64_string.split(",", 1)[1]

        image_data = base64.b64decode(base64_string)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(image_data)
        logger.success(f"Изображение сохранено: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении изображения: {e}")
        return False


def generate_image(prompt: str, model: str = "google/gemini-2.5-flash-image",
                   aspect_ratio: str = "16:9", image_size: str = "1K",
                   output_dir: str = "generated_images") -> bool:
    """
    Генерирует изображение через OpenRouter API.

    Args:
        prompt: Текстовый запрос для генерации
        model: Название модели (по умолчанию google/gemini-3.1-flash-image-preview)
        aspect_ratio: Соотношение сторон (1:1, 16:9, 9:16 и др.)
        image_size: Качество (0.5K, 1K, 2K, 4K)
        output_dir: Директория для сохранения результатов
    """
    if not api_key:
        logger.error("OPENROUTER_API_KEY не найден в переменных окружения")
        return False

    proxies = setup_proxy()

    # Исправленный URL без пробелов в конце
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-url.com",  # Опционально, рекомендуется OpenRouter
        "X-Title": "Image Generator Bot"  # Опционально
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "modalities": ["image", "text"],  # Запрашиваем и текст, и изображение
        "image_config": {
            "aspect_ratio": aspect_ratio,
            "image_size": image_size
        }
    }

    try:
        logger.info(f"Отправка запроса на генерацию: {prompt[:50]}...")
        response = requests.post(
            url=url,
            headers=headers,
            json=payload,  # requests автоматически сериализует JSON
            proxies=proxies,
            timeout=120  # Генерация изображений может занимать время
        )
        response.raise_for_status()
        result = response.json()

        # Проверка на ошибки в ответе OpenRouter
        if "error" in result:
            error_msg = result.get("error", {}).get("message", "Неизвестная ошибка")
            logger.error(f"API Error: {error_msg}")
            return False

        if not result.get("choices"):
            logger.warning("Пустой ответ от API (нет choices)")
            return False

        message = result["choices"][0].get("message", {})

        # Вывод текстовой части ответа (если есть)
        if content := message.get("content"):
            logger.info(f"Ответ модели: {content}")

        # Обработка изображений
        if images := message.get("images"):
            logger.success(f"Сгенерировано изображений: {len(images)}")
            for idx, image in enumerate(images, 1):
                image_url = image.get("image_url", {}).get("url", "")
                if image_url:
                    # Показываем превью base64 строки
                    preview = image_url[:60] + "..." if len(image_url) > 60 else image_url
                    logger.info(f"Изображение #{idx}: {preview}")

                    # Сохраняем на диск
                    filename = f"img_{prompt[:20].replace(' ', '_')}_{idx}.png"
                    save_path = Path(output_dir) / filename
                    save_base64_image(image_url, str(save_path))
            return True
        else:
            logger.warning("В ответе нет поля 'images'")
            return False

    except requests.exceptions.Timeout:
        logger.error("Тайм-аут запроса. Попробуйте увеличить timeout или проверить соединение.")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Ошибка соединения. Проверьте прокси и интернет-соединение.")
        return False
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP ошибка {e.response.status_code}: {e.response.text}")
        return False
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка: {e}")
        return False


if __name__ == '__main__':
    # Пример использования
    input_prompt = input("\nВведите ваш промт:\t\t").strip().lower()

    success = generate_image(
        prompt=input_prompt,
        aspect_ratio="16:9",  # Поддерживаемые: 1:1, 16:9, 9:16, 4:3, 3:4 и др.
        image_size="1K"  # Поддерживаемые: 0.5K (только Gemini), 1K, 2K, 4K
    )

    if success:
        print("✅ Генерация завершена успешно!")
    else:
        print("❌ Ошибка при генерации изображения")
