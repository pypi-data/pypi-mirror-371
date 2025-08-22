import os
import sys
from .main import main as app_main

def main():
    """Точка входа для консольной команды"""
    # Добавляем текущую директорию в путь для импорта
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    app_main()

if __name__ == "__main__":
    main()