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


def load_image_as_base64(image_path: str) -> tuple[str, str]:
    """
    Загружает изображение с диска и конвертирует в base64.
    Возвращает (base64_string, mime_type).
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {image_path}")

    # Определяем MIME-тип по расширению
    ext = path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime_type = mime_map.get(ext, "image/png")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    logger.info(f"Изображение загружено: {image_path} ({mime_type})")
    return encoded, mime_type


def save_base64_image(base64_string: str, output_path: str):
    """Сохраняет base64-строку как изображение в файл."""
    try:
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


def edit_image(
        image_path: str,
        prompt: str,
        model: str = "google/gemini-3.1-flash-image-preview",
        aspect_ratio: str = "16:9",
        image_size: str = "1K",
        output_dir: str = "edited_images"
) -> bool:
    """
    Редактирует существующее изображение по текстовому промту через OpenRouter API.

    Args:
        image_path:   Путь к исходному изображению на диске
        prompt:       Инструкция по редактированию (что изменить)
        model:        Модель (должна поддерживать vision + image output)
        aspect_ratio: Соотношение сторон результата
        image_size:   Качество результата (0.5K, 1K, 2K, 4K)
        output_dir:   Папка для сохранения результата
    """
    if not api_key:
        logger.error("OPENROUTER_API_KEY не найден в переменных окружения")
        return False

    # Загружаем исходное изображение
    try:
        b64_image, mime_type = load_image_as_base64(image_path)
    except FileNotFoundError as e:
        logger.error(e)
        return False

    proxies = setup_proxy()

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-url.com",
        "X-Title": "Image Editor Bot"
    }

    # Передаём изображение + текстовый промт в одном сообщении
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{b64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "modalities": ["image", "text"],
        "image_config": {
            "aspect_ratio": aspect_ratio,
            "image_size": image_size
        }
    }

    try:
        logger.info(f"Отправка запроса на редактирование: {prompt[:60]}...")
        response = requests.post(
            url=url,
            headers=headers,
            json=payload,
            proxies=proxies,
            timeout=180
        )
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            error_msg = result.get("error", {}).get("message", "Неизвестная ошибка")
            logger.error(f"API Error: {error_msg}")
            return False

        if not result.get("choices"):
            logger.warning("Пустой ответ от API (нет choices)")
            logger.debug(f"Полный ответ: {result}")
            return False

        message = result["choices"][0].get("message", {})

        # Текстовая часть ответа
        if content := message.get("content"):
            logger.info(f"Ответ модели: {content}")

        # Сохраняем полученное изображение
        if images := message.get("images"):
            logger.success(f"Получено изображений: {len(images)}")
            source_name = Path(image_path).stem
            for idx, image in enumerate(images, 1):
                image_url = image.get("image_url", {}).get("url", "")
                if image_url:
                    filename = f"{source_name}_edited_{idx}.png"
                    save_path = Path(output_dir) / filename
                    save_base64_image(image_url, str(save_path))
            return True
        else:
            logger.warning("В ответе нет поля 'images'. Полный ответ:")
            logger.debug(result)
            return False

    except requests.exceptions.Timeout:
        logger.error("Тайм-аут запроса. Попробуйте увеличить timeout.")
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
    print("=== Редактор изображений ===\n")

    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)

    # Ищем изображения в папке input
    supported_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    images_in_input = [f for f in input_dir.iterdir() if f.suffix.lower() in supported_extensions]

    if not images_in_input:
        print(f"❌ В папке '{input_dir}' нет изображений. Поместите файл и запустите снова.")
        exit(1)

    # Если файлов несколько — показываем список и даём выбрать
    if len(images_in_input) == 1:
        selected = images_in_input[0]
        print(f"Найдено изображение: {selected.name}")
    else:
        print("Найдены изображения:")
        for i, f in enumerate(images_in_input, 1):
            print(f"  {i}. {f.name}")
        choice = input("Выберите номер файла: ").strip()
        selected = images_in_input[int(choice) - 1]

    edit_prompt = input("Что нужно изменить (промт):\t").strip()

    success = edit_image(
        image_path=str(selected),
        prompt=edit_prompt,
        aspect_ratio="16:9",  # 1:1, 16:9, 9:16, 4:3, 3:4
        image_size="1K"  # 0.5K, 1K, 2K, 4K
    )

    if success:
        print("\n✅ Редактирование завершено успешно!")
    else:
        print("\n❌ Ошибка при редактировании изображения")
