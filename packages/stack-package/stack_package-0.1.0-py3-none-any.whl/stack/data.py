"""
Модуль для работы с данными из test.txt
"""

import os
import pkg_resources

def get_content():
    """
    Возвращает содержимое файла test.txt
    
    Returns:
        str: Содержимое файла test.txt
    """
    try:
        # Получаем путь к файлу test.txt в пакете
        file_path = pkg_resources.resource_filename('yar', 'test.txt')
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        return f"Ошибка чтения файла: {e}"

def get_file_path():
    """
    Возвращает путь к файлу test.txt в пакете
    
    Returns:
        str: Путь к файлу test.txt
    """
    return pkg_resources.resource_filename('yar', 'test.txt') 