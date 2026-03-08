import os
import base64
import json
import requests
from dotenv import load_dotenv

load_dotenv()


def save_base64_image(base64_string, filename="generated_image.png"):
    """Сохраняет base64 изображение в файл."""
    if "base64," in base64_string:
        base64_string = base64_string.split("base64,")[1]

    image_data = base64.b64decode(base64_string)

    with open(filename, "wb") as f:
        f.write(image_data)

    print(f"✅ Изображение сохранено: {filename}")
    return filename


def generate_image_polza(prompt, model="google/gemini-2.5-flash-image"):
    """Генерирует изображение через polza.ai (chat completions endpoint)."""

    api_key = os.getenv("POLZA_AI_API_KEY")

    if not api_key:
        raise ValueError("POLZA_AI_API_KEY не найден в .env!")

    print(f"🚀 Генерация изображения: {prompt}")
    print(f"📦 Модель: {model}")

    # Используем CHAT COMPLETIONS endpoint (как в вашем рабочем коде!)
    response = requests.post(
        url="https://api.polza.ai/api/v1/chat/completions",  # ← НЕ /images/generate!
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "modalities": ["image", "text"]  # ← КЛЮЧЕВОЙ параметр для Gemini!
        }
    )

    print(f"📡 Status code: {response.status_code}")

    if response.status_code != 200:
        print(f"❌ Ошибка API: {response.text}")
        raise Exception(f"API error: {response.status_code}")

    result = response.json()
    print(f"📋 Полный ответ: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")

    # Извлекаем изображения (как в вашем рабочем коде)
    if result.get("choices"):
        message = result["choices"][0]["message"]

        # Текстовый ответ
        if message.get("content"):
            print(f"💬 Текст: {message['content']}")

        # Изображения
        if message.get("images"):
            images = []
            for idx, image in enumerate(message["images"]):
                image_url = image["image_url"]["url"]
                filename = f"polza_generated_{idx + 1}.png"
                saved_file = save_base64_image(image_url, filename)
                images.append(saved_file)
                print(f"✅ Изображение {idx + 1}: {saved_file}")

            return images
        else:
            print("⚠️ Изображения не найдены в ответе")
            return None
    else:
        print("❌ Некорректный ответ от API")
        return None


# ТЕСТ
if __name__ == "__main__":
    try:
        prompt = "A cute baby sea otter"

        # Попробуем разные модели
        models = [
            "google/gemini-2.5-flash-image",
            "google/gemini-3-pro-image-preview",
            "google/gemini-2.5-pro-image",
        ]

        for model in models:
            try:
                print(f"\n{'=' * 60}")
                print(f"🧪 Тестирую модель: {model}")
                print(f"{'=' * 60}")

                images = generate_image_polza(prompt, model=model)

                if images:
                    print(f"\n🎉 УСПЕХ! Модель {model} работает!")
                    print(f"📁 Сохранено файлов: {len(images)}")
                    break  # Первая рабочая модель найдена!

            except Exception as e:
                print(f"❌ {model}: {str(e)[:200]}")
                continue

    except Exception as e:
        print(f"\n❌ Общая ошибка: {e}")
        import traceback

        traceback.print_exc()
