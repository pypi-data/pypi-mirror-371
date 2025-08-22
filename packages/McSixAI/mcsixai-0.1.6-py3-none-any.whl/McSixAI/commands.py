import re
from .file_manager import FileManager


class CommandProcessor:
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.commands = {
            'read': self.handle_read,
            'write': self.handle_write,
            'list': self.handle_list,
            'structure': self.handle_structure,
            'find': self.handle_find,
            'create': self.handle_create,
            'solve': self.handle_solve
        }

    def process_command(self, user_input: str) -> str:
        """Обрабатывает специальные команды"""
        # Проверяем, является ли ввод командой
        for cmd in self.commands:
            if user_input.strip().startswith(f'/{cmd}'):
                return self.commands[cmd](user_input)
        return None

    def handle_read(self, input_text: str) -> str:
        """Чтение файла: /read filename.py"""
        match = re.match(r'/read\s+(\S+)', input_text)
        if match:
            filename = match.group(1)
            return self.file_manager.read_file(filename)
        return "Неверный формат команды. Используйте: /read filename.py"

    def handle_write(self, input_text: str) -> str:
        """Запись в файл: /write filename.py\n```content```"""
        match = re.match(r'/write\s+(\S+)\s*(.*)', input_text, re.DOTALL)
        if match:
            filename = match.group(1)
            # Ищем код между ``` или получаем весь остальной текст
            code_match = re.search(r'```(?:\w+)?\n?(.*?)```', input_text, re.DOTALL)
            if code_match:
                content = code_match.group(1)
            else:
                content = match.group(2)
            return self.file_manager.write_file(filename, content)
        return "Неверный формат команды. Используйте: /write filename.py\n```content```"

    def handle_solve(self, input_text: str) -> str:
        """Решение задачи из файла: /solve filename.txt"""
        match = re.match(r'/solve\s+(\S+)', input_text)
        if match:
            filename = match.group(1)
            # Читаем условие задачи из файла
            problem_statement = self.file_manager.read_file(filename)

            if "Ошибка чтения" in problem_statement:
                return problem_statement

            # Отправляем нейросети полный текст
            return f"Решаю задачу из файла {filename}...\n{problem_statement}"
        return "Неверный формат. Используйте: /solve task.txt"

    def handle_list(self, input_text: str) -> str:
        """Список файлов: /list"""
        files = self.file_manager.list_files()
        return "Файлы в проекте:\n" + "\n".join(files)

    def handle_structure(self, input_text: str) -> str:
        """Структура проекта: /structure"""
        return self.file_manager.get_project_structure()

    def handle_find(self, input_text: str) -> str:
        """Поиск в файлах: /find search_term"""
        match = re.match(r'/find\s+(.+)', input_text)
        if match:
            search_term = match.group(1)
            results = self.file_manager.find_in_files(search_term)
            if not results:
                return f"Ничего не найдено для: {search_term}"

            output = []
            for file, matches in results.items():
                output.append(f"📁 {file}:")
                output.extend(matches[:3])  # Показываем первые 3 совпадения
                if len(matches) > 3:
                    output.append(f"  ... и еще {len(matches) - 3} совпадений")
            return "\n".join(output)
        return "Неверный формат команды. Используйте: /find search_term"

    def handle_create(self, input_text: str) -> str:
        """Создание файла: /create filename.py\n```content```"""
        return self.handle_write(input_text.replace('/create', '/write'))

