#!/usr/bin/env python3
"""
🔍 Z-Library Search and Download Example
Использует JSON API для поиска и загрузки книг
"""

import subprocess
import json
import sys
import os
from pathlib import Path

# Настройки
PROJECT_ROOT = Path(__file__).parent.parent.parent  # examples/python -> project root
API_SCRIPT = PROJECT_ROOT / "scripts" / "zlib_book_search.sh"
DOWNLOAD_DIR = PROJECT_ROOT / "examples" / "downloads"

def run_api_command(cmd_args):
    """Выполнить команду API и вернуть JSON результат"""
    cmd = [str(API_SCRIPT)] + cmd_args
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        # Попробовать распарсить JSON из stdout
        if result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"status": "error", "message": f"Invalid JSON response: {result.stdout}"}
        
        # Если stdout пустой, проверить stderr
        if result.stderr.strip():
            try:
                return json.loads(result.stderr)
            except json.JSONDecodeError:
                return {"status": "error", "message": f"Error: {result.stderr}"}
        
        return {"status": "error", "message": "No response from API"}
        
    except Exception as e:
        return {"status": "error", "message": f"Command failed: {e}"}

def search_books(query, format_type="epub", language="english", count=5):
    """Поиск книг с фильтрами"""
    print(f"🔍 Поиск: '{query}' (формат: {format_type}, язык: {language})")
    
    cmd_args = [
        "--json",
        "-f", format_type,
        "-l", language, 
        "-c", str(count),
        query
    ]
    
    result = run_api_command(cmd_args)
    
    if result["status"] == "success":
        print(f"✅ Найдено {result['total_results']} книг:")
        books = result["results"]
        
        for i, book in enumerate(books, 1):
            authors = ", ".join(book.get("authors", ["Unknown"]))
            size = book.get("size", "Unknown")
            year = book.get("year", "Unknown")
            rating = book.get("rating", "Unknown")
            
            print(f"  {i}. 📚 {book['name']}")
            print(f"     👥 Авторы: {authors}")
            print(f"     📅 Год: {year}")
            print(f"     💾 Размер: {size}")
            print(f"     ⭐ Рейтинг: {rating}")
            print()
        
        return books
    else:
        print(f"❌ Ошибка поиска: {result['message']}")
        return []

def download_book(query, format_type="epub", language="english", output_dir=None):
    """Загрузить первую найденную книгу"""
    if output_dir is None:
        output_dir = DOWNLOAD_DIR
    
    print(f"⬇️ Загрузка: '{query}' в {output_dir}")
    
    # Создать директорию если не существует
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    cmd_args = [
        "--json",
        "--download",
        "-f", format_type,
        "-l", language,
        "-o", str(output_dir),
        query
    ]
    
    result = run_api_command(cmd_args)
    
    if result["status"] == "success":
        book_info = result["book"]
        file_info = result["file"]
        
        print(f"✅ Загружено: {book_info['name']}")
        print(f"📄 Файл: {file_info['path']}")
        print(f"💾 Размер: {file_info['size']:,} байт")
        
        return file_info["path"]
    else:
        print(f"❌ Ошибка загрузки: {result['message']}")
        return None

def check_limits():
    """Проверить лимиты загрузки"""
    print("📊 Проверка лимитов...")
    
    result = run_api_command(["--json", "--limits"])
    
    if result["status"] == "success":
        limits = result["limits"]
        warnings = result.get("warnings", [])
        
        print(f"📈 Дневной лимит: {limits['daily_allowed']}")
        print(f"🔄 Остается: {limits['daily_remaining']}")
        print(f"🕐 Сброс через: {limits['daily_reset']} часов")
        
        if warnings:
            for warning in warnings:
                print(f"⚠️ {warning}")
        
        return limits["daily_remaining"] > 0
    else:
        print(f"❌ Ошибка проверки лимитов: {result['message']}")
        return False

def select_book_interactive(books):
    """Интерактивный выбор книги"""
    if not books:
        return None
    
    print("\n📋 Выберите книгу для загрузки:")
    for i, book in enumerate(books, 1):
        print(f"  {i}. {book['name']}")
    
    while True:
        try:
            choice = input(f"\nВведите номер (1-{len(books)}) или 'q' для выхода: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(books):
                selected_book = books[choice_num - 1]
                print(f"✅ Выбрана: {selected_book['name']}")
                return selected_book
            else:
                print(f"❌ Введите число от 1 до {len(books)}")
        
        except ValueError:
            print("❌ Введите корректный номер")
        except KeyboardInterrupt:
            print("\n👋 Выход...")
            return None

def main():
    """Основная функция - демонстрация API"""
    print("🚀 Z-Library API Example - Поиск и загрузка книг")
    print("=" * 50)
    
    # Проверить доступность API
    if not API_SCRIPT.exists():
        print(f"❌ API скрипт не найден: {API_SCRIPT}")
        return 1
    
    # Проверить лимиты
    print("\n1️⃣ Проверка лимитов загрузки:")
    has_quota = check_limits()
    
    if not has_quota:
        print("⚠️ Лимит загрузки исчерпан!")
        return 1
    
    # Поиск книг
    print("\n2️⃣ Поиск книг:")
    
    # Примеры поисков
    search_queries = [
        {"query": "python programming", "format": "epub", "language": "english"},
        {"query": "машинное обучение", "format": "epub", "language": "russian"},
        {"query": "data science", "format": "pdf", "language": "english"}
    ]
    
    all_books = []
    
    for search in search_queries:
        print(f"\n🔍 Поиск: {search['query']}")
        books = search_books(
            search["query"], 
            search["format"], 
            search["language"], 
            count=3
        )
        
        if books:
            # Добавить информацию о поиске к каждой книге
            for book in books:
                book["_search_query"] = search["query"]
                book["_search_format"] = search["format"]
                book["_search_language"] = search["language"]
            
            all_books.extend(books)
    
    if not all_books:
        print("❌ Книги не найдены!")
        return 1
    
    # Интерактивный выбор
    print(f"\n3️⃣ Выбор книги для загрузки:")
    print(f"Найдено всего {len(all_books)} книг")
    
    # Автоматический выбор первой книги для демо
    selected_book = all_books[0]
    print(f"🎯 Автоматически выбрана первая книга: {selected_book['name']}")
    
    # Можно включить интерактивный режим:
    # selected_book = select_book_interactive(all_books)
    
    if not selected_book:
        print("👋 Выход без загрузки")
        return 0
    
    # Загрузка выбранной книги
    print(f"\n4️⃣ Загрузка выбранной книги:")
    
    # Создать уникальную директорию для загрузки
    book_dir = DOWNLOAD_DIR / "epub_books"
    
    # Использовать параметры из поиска
    downloaded_file = download_book(
        selected_book["_search_query"],
        selected_book["_search_format"], 
        selected_book["_search_language"],
        book_dir
    )
    
    if downloaded_file:
        print(f"\n🎉 Загрузка завершена!")
        print(f"📁 Файл: {downloaded_file}")
        
        # Вернуть путь к файлу для дальнейшей диагностики
        return downloaded_file
    else:
        print("\n❌ Загрузка не удалась")
        return 1

if __name__ == "__main__":
    try:
        result = main()
        if isinstance(result, str):
            print(f"\n📋 Результат: {result}")
            sys.exit(0)
        else:
            sys.exit(result)
    except KeyboardInterrupt:
        print("\n👋 Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        sys.exit(1)