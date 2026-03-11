import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent

# Функция для получения переменных окружения
def get_env_variable(key, default=None):
    """Получение переменной окружения или возврат значения по умолчанию"""
    value = os.getenv(key, default)
    if value is None:
        raise Exception(f"Переменная окружения {key} не установлена")
    return value
