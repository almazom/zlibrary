#!/usr/bin/env python3
"""
🚀 Полный пример: Поиск → Загрузка → Диагностика EPUB
Демонстрирует весь workflow работы с Z-Library API
"""

import subprocess
import sys
import os
from pathlib import Path

# Настройки  
PROJECT_ROOT = Path(__file__).parent.parent  # examples -> project root
PYTHON_DIR = Path(__file__).parent / "python"  # examples/python
DOWNLOAD_DIR = Path(__file__).parent / "downloads" / "full_example"

def run_python_script(script_name, args=None):
    """Запустить Python скрипт и вернуть результат"""
    script_path = PYTHON_DIR / script_name
    
    if not script_path.exists():
        print(f"❌ Скрипт не найден: {script_path}")
        return None
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=PROJECT_ROOT
        )
        
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        print(f"❌ Ошибка выполнения {script_name}: {e}")
        return None

def find_downloaded_files(directory):
    """Найти все загруженные EPUB файлы"""
    epub_files = []
    
    if not Path(directory).exists():
        return epub_files
    
    for file_path in Path(directory).rglob("*.epub"):
        epub_files.append(file_path)
    
    return epub_files

def main():
    """Основная функция - полный workflow"""
    print("🚀 Z-Library Full Workflow Example")
    print("=" * 50)
    print("Этапы:")
    print("1️⃣ Поиск и загрузка книги через JSON API")
    print("2️⃣ Диагностика качества загруженного EPUB")
    print("3️⃣ Итоговый отчет")
    print()
    
    # Создать директорию для загрузок
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Этап 1: Поиск и загрузка
    print("🔍 ЭТАП 1: Поиск и загрузка книги")
    print("-" * 30)
    
    search_result = run_python_script("search_and_download.py")
    
    if not search_result:
        print("❌ Не удалось запустить поиск и загрузку")
        return 1
    
    if search_result['returncode'] != 0:
        print("❌ Ошибка поиска/загрузки:")
        print(search_result['stderr'] or search_result['stdout'])
        return 1
    
    print("✅ Поиск и загрузка завершены")
    
    # Найти загруженный файл
    downloaded_files = find_downloaded_files(DOWNLOAD_DIR.parent)
    
    if not downloaded_files:
        print("❌ Не найдены загруженные EPUB файлы")
        print("Проверьте директорию:", DOWNLOAD_DIR.parent)
        return 1
    
    # Выбрать самый свежий файл
    latest_file = max(downloaded_files, key=lambda f: f.stat().st_mtime)
    
    print(f"📁 Найден EPUB файл: {latest_file.name}")
    print(f"💾 Размер: {latest_file.stat().st_size:,} байт")
    print()
    
    # Этап 2: Диагностика EPUB
    print("📖 ЭТАП 2: Диагностика EPUB файла")
    print("-" * 30)
    
    diagnostic_result = run_python_script("epub_diagnostics.py", [str(latest_file)])
    
    if not diagnostic_result:
        print("❌ Не удалось запустить диагностику")
        return 1
    
    # Показать результат диагностики
    print(diagnostic_result['stdout'])
    
    if diagnostic_result['stderr']:
        print("⚠️ Предупреждения диагностики:")
        print(diagnostic_result['stderr'])
    
    # Этап 3: Итоговый отчет
    print("\n🎯 ЭТАП 3: Итоговый отчет")
    print("-" * 30)
    
    # Определить результат на основе кода возврата диагностики
    diagnostic_code = diagnostic_result['returncode']
    
    if diagnostic_code == 0:
        quality_status = "🟢 ВЫСОКОЕ КАЧЕСТВО"
        recommendation = "✅ Файл готов к использованию"
    elif diagnostic_code == 1:
        quality_status = "🟡 СРЕДНЕЕ КАЧЕСТВО"
        recommendation = "⚠️ Возможны небольшие проблемы при чтении"
    else:
        quality_status = "🔴 НИЗКОЕ КАЧЕСТВО"
        recommendation = "❌ Рекомендуется найти другую версию"
    
    print(f"📊 Качество EPUB: {quality_status}")
    print(f"💡 Рекомендация: {recommendation}")
    print()
    
    # Статистика
    print("📈 СТАТИСТИКА:")
    print(f"   • Файл: {latest_file.name}")
    print(f"   • Путь: {latest_file}")
    print(f"   • Размер: {latest_file.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"   • Код качества: {diagnostic_code}")
    print()
    
    # Дальнейшие действия
    print("🔧 ДАЛЬНЕЙШИЕ ДЕЙСТВИЯ:")
    
    if diagnostic_code == 0:
        print("   ✅ Файл можно использовать в любой читалке")
        print("   📱 Совместим с большинством устройств")
        print("   🎉 Наслаждайтесь чтением!")
    elif diagnostic_code == 1:
        print("   📖 Попробуйте открыть в разных читалках")
        print("   🔍 При проблемах - поищите другую версию")
        print("   ⚙️ Возможно потребуется конвертация")
    else:
        print("   🔄 Повторите поиск с другими параметрами")
        print("   📚 Попробуйте другой формат (PDF вместо EPUB)")
        print("   🌍 Поищите на других языках")
    
    print()
    print("="*50)
    print("✨ Workflow завершен!")
    
    return diagnostic_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        sys.exit(1)