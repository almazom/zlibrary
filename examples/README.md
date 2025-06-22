# 🚀 Z-Library API Examples

Практические примеры использования Z-Library CLI API для поиска, загрузки и анализа книг.

## 📁 Структура

```
examples/
├── python/
│   ├── search_and_download.py    # Поиск и загрузка книг
│   └── epub_diagnostics.py       # Диагностика качества EPUB
├── run_full_example.py           # Полный workflow
├── test_epub_diagnostics.py      # Тест диагностики
└── README.md                     # Эта документация
```

## 🎯 Примеры использования

### 1. 🧪 Тест диагностики EPUB (без credentials)

Не требует настройки Z-Library аккаунта:

```bash
cd examples
python3 test_epub_diagnostics.py
```

**Что делает:**
- 🏗️ Создает тестовые EPUB файлы (хороший и плохой)
- 📖 Анализирует их качество
- 📊 Показывает подробные отчеты

### 2. 🔍 Поиск и загрузка (требует credentials)

```bash
# Настроить credentials в .env файле
cd examples/python
python3 search_and_download.py
```

**Что делает:**
- 🔍 Ищет книги по различным запросам
- 📋 Показывает результаты поиска
- ⬇️ Загружает выбранную книгу в EPUB формате
- 📁 Сохраняет в `downloads/examples/epub_books/`

### 3. 🚀 Полный workflow

```bash
cd examples  
python3 run_full_example.py
```

**Полный цикл:**
1. 🔍 Поиск книг через JSON API
2. ⬇️ Загрузка первой найденной книги
3. 📖 Диагностика качества EPUB
4. 📊 Итоговый отчет с рекомендациями

## 📖 Диагностика EPUB

### Что проверяется:

#### ✅ Структурная валидность
- 📦 ZIP архив корректный
- 📄 Обязательные файлы (`mimetype`, `container.xml`)
- 🏗️ OPF манифест и spine
- 🔗 Целостность ссылок

#### 📚 Содержимое
- 📝 HTML/XHTML файлы контента
- 🎨 CSS стили
- 🖼️ Изображения
- 📋 Метаданные (название, автор, язык)

#### 🎯 Оценка качества (0-100 баллов)
- 🟢 **80-100**: Отличное качество
- 🟡 **60-79**: Хорошее качество  
- 🟠 **40-59**: Удовлетворительное
- 🔴 **0-39**: Плохое качество

### Пример отчета:

```
📖 Анализ EPUB: Python_Programming_Guide.epub
==================================================
✅ ZIP структура: 15 файлов
✅ MIME type: корректный
✅ Container.xml: OPF файл найден
📚 Название: Python Programming Guide
👤 Автор: John Doe
🌍 Язык: English
📋 Манифест: 12 элементов
📖 Spine: 8 глав
📄 Контент: 8 HTML, 2 CSS
🖼️ Изображения: 5 файлов
📊 Размер файла: 2,450,123 байт (2.3 MB)
📈 Оценка качества: 95/100

🎯 КАЧЕСТВО EPUB: 🟢 ОТЛИЧНОЕ (95/100)

💡 РЕКОМЕНДАЦИИ:
   ✅ EPUB файл высокого качества, готов к использованию
```

## ⚙️ Настройка

### 1. Credentials для Z-Library

Создайте файл `.env` в корне проекта:

```bash
cp env.template .env
# Отредактируйте .env и добавьте свои данные:
ZLOGIN=your-email@example.com
ZPASSW=your-password
```

### 2. Зависимости

```bash
pip install aiohttp aiofiles
```

### 3. Проверка API

```bash
cd scripts
./zlib_book_search.sh --json --limits
```

## 🔧 API Commands

### Поиск книг

```bash
# Базовый поиск
./zlib_book_search.sh --json "python programming"

# С фильтрами
./zlib_book_search.sh --json -f epub -l english -c 5 "machine learning"

# Загрузка
./zlib_book_search.sh --json --download -o downloads "data science"
```

### JSON Response структура

#### Успешный поиск:
```json
{
  "status": "success",
  "query": "python programming",
  "total_results": 10,
  "page": 1,
  "total_pages": 5,
  "results": [
    {
      "id": "123456/abcdef",
      "name": "Python Programming Guide",
      "authors": ["John Doe"],
      "year": "2023",
      "extension": "epub",
      "size": "2.5 MB",
      "rating": "4.5/5.0"
    }
  ]
}
```

#### Успешная загрузка:
```json
{
  "status": "success",
  "message": "Download completed successfully",
  "book": {
    "name": "Python Programming Guide",
    "id": "123456/abcdef",
    "extension": "epub",
    "size_bytes": 2621440
  },
  "file": {
    "path": "./downloads/Python Programming Guide.epub",
    "size": 2621440
  }
}
```

## 🐛 Troubleshooting

### Проблемы с поиском/загрузкой

```bash
# Проверить credentials
./zlib_book_search.sh --json --limits

# Проверить зависимости
python3 -c "import aiohttp, aiofiles; print('OK')"

# Тестовый поиск
./zlib_book_search.sh --json -c 1 "test"
```

### Проблемы с EPUB

```bash
# Тест диагностики
python3 test_epub_diagnostics.py

# Ручная диагностика файла
python3 python/epub_diagnostics.py /path/to/book.epub
```

### Логи и отладка

```bash
# Verbose режим
./zlib_book_search.sh -v --json "query"

# Проверить структуру ответа
./zlib_book_search.sh --json "test" | jq '.'
```

## 📊 Статистика использования

После запуска примеров вы получите:

- 📁 **Загруженные файлы**: `downloads/examples/`
- 📖 **EPUB файлы**: готовые к чтению
- 📋 **Отчеты качества**: детальный анализ
- 🎯 **Рекомендации**: что делать с файлом

## 🔮 Интеграция в проекты

### Python интеграция

```python
import subprocess
import json

def search_books(query):
    result = subprocess.run([
        './zlib_book_search.sh', '--json', query
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)

# Использование
books = search_books("python programming")
if books["status"] == "success":
    for book in books["results"]:
        print(f"📚 {book['name']}")
```

### Bash интеграция

```bash
#!/bin/bash
search_and_analyze() {
    local query="$1"
    
    # Поиск и загрузка
    result=$(./zlib_book_search.sh --json --download "$query")
    
    # Извлечь путь к файлу
    file_path=$(echo "$result" | jq -r '.file.path')
    
    # Диагностика
    if [[ -f "$file_path" ]]; then
        python3 python/epub_diagnostics.py "$file_path"
    fi
}
```

## 🎉 Ready to go!

Все готово для поиска, загрузки и анализа книг! 

**Быстрый старт:**
1. 🔧 Настройте `.env` с credentials
2. 🧪 Запустите `python3 test_epub_diagnostics.py`
3. 🚀 Попробуйте `python3 run_full_example.py`

**Happy reading!** 📚✨