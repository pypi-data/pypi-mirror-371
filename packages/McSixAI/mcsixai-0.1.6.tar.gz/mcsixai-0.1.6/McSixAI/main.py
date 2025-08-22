import os

from .openrouter import OpenRouterAPI
from .file_manager import FileManager
from .commands import CommandProcessor
from .config import OPENROUTER_API_KEY


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════╗
    ║               McSix AI PRO                       ║
    ║    developer: McSix                              ║
    ║                    Telegram: @McSixRu            ║
    ╚══════════════════════════════════════════════════╝
    """
    print(banner)


def check_config():
    if not OPENROUTER_API_KEY:
        print("❌ ОШИБКА: API ключ не найден!")
        print("1. Создайте файл .env в папке проекта")
        print("2. Добавьте строку: OPENROUTER_API_KEY=ваш_ключ_здесь")
        print("3. Получите ключ на https://openrouter.ai/")
        return False
    return True


def main():
    clear_screen()
    print_banner()

    if not check_config():
        return

    # Инициализация менеджера файлов и процессора команд
    file_manager = FileManager()
    command_processor = CommandProcessor(file_manager)
    api = OpenRouterAPI()

    print("Добро пожаловать в CodeAssist AI Pro!")
    print("Доступные команды:")
    print("  /read filename.py    - прочитать файл")
    print("  /write filename.py   - записать в файл")
    print("  /create filename.py  - создать файл")
    print("  /list               - список файлов")
    print("  /structure          - структура проекта")
    print("  /find term          - поиск в файлах")
    print("  /quit               - выход\n")

    while True:
        try:
            user_input = input("👤 Вы: ")

            if user_input.lower() in ['quit', 'exit', 'q', '/quit']:
                print("До свидания!")
                break

            if not user_input.strip():
                continue

            # Обрабатываем команды
            command_result = command_processor.process_command(user_input)
            if command_result:
                print(f"🤖 Система: {command_result}\n")
                continue

            # Очищаем историю перед каждым запросом
            current_messages = [
                {
                    "role": "system",
                    "content": """Ты - AI ассистент для программирования. Ты помогаешь с написанием кода, 
                    рефакторингом, поиском ошибок. Ты имеешь доступ к файловой системе через специальные команды.
                    Будь полезным и точным в ответах."""
                },
                {"role": "user", "content": user_input}
            ]

            print("🤖 AI: ", end="", flush=True)
            response = api.generate_response(current_messages)
            print(response)  # Теперь будет выводиться ТОЛЬКО ответ нейросети
            print()

        except KeyboardInterrupt:
            print("\n\nДо свидания!")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {str(e)}")
            print("Попробуйте еще раз...\n")


if __name__ == "__main__":
    main()