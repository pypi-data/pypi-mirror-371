import os
import glob
import re
from typing import List, Dict


class FileManager:
    def __init__(self, base_path="."):
        self.base_path = base_path
        self.current_file = None

    def read_file(self, file_path: str) -> str:
        """Читает содержимое файла"""
        try:
            full_path = os.path.join(self.base_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Ошибка чтения файла: {str(e)}"

    def write_file(self, file_path: str, content: str) -> str:
        """Записывает содержимое в файл"""
        try:
            full_path = os.path.join(self.base_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Файл {file_path} успешно записан"
        except Exception as e:
            return f"Ошибка записи файла: {str(e)}"

    def list_files(self, pattern="*") -> List[str]:
        """Список файлов в проекте"""
        files = []
        for root, _, filenames in os.walk(self.base_path):
            for filename in filenames:
                if filename.endswith('.py') or filename.endswith('.txt') or filename.endswith('.md'):
                    rel_path = os.path.relpath(os.path.join(root, filename), self.base_path)
                    files.append(rel_path)
        return files

    def get_project_structure(self) -> str:
        """Возвращает структуру проекта"""
        structure = []
        for root, dirs, files in os.walk(self.base_path):
            level = root.replace(self.base_path, '').count(os.sep)
            indent = ' ' * 2 * level
            structure.append(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith(('.py', '.txt', '.md', '.json')):
                    structure.append(f"{subindent}{file}")
        return "\n".join(structure)

    def find_in_files(self, search_term: str) -> Dict[str, List[str]]:
        """Поиск текста в файлах проекта"""
        results = {}
        for file_path in self.list_files():
            content = self.read_file(file_path)
            if search_term in content:
                lines = content.split('\n')
                matches = [f"Line {i + 1}: {line}" for i, line in enumerate(lines) if search_term in line]
                results[file_path] = matches
        return results