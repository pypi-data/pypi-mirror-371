import requests
import json
from .config import OPENROUTER_API_KEY, OPENROUTER_MODEL, SITE_URL, SITE_NAME


class OpenRouterAPI:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate_response(self, messages):
        """Отправляет запрос к OpenRouter API и возвращает ответ"""
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Please set OPENROUTER_API_KEY in your environment variables.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
        }

        data = {
            "model": self.model,
            "messages": messages,
        }

        try:

            response = requests.post(
                url=self.base_url,
                headers=headers,
                json=data  # Используем json вместо data=json.dumps()
            )

            print(f"Статус ответа: {response.status_code}")

            # Если ошибка, выведем подробности
            if response.status_code != 200:
                print(f"Текст ошибки: {response.text}")
                response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            return f"Ошибка при запросе к API: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Ошибка при обработке ответа API: {str(e)}"