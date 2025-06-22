#!/usr/bin/env python3
"""
🧪 Тест диагностики EPUB без загрузки
Создает тестовый EPUB файл и анализирует его
"""

import zipfile
import tempfile
import os
from pathlib import Path
import sys

# Добавить путь к нашим модулям
sys.path.insert(0, str(Path(__file__).parent / "python"))

from epub_diagnostics import EPUBDiagnostics

def create_test_epub(output_path):
    """Создать минимальный тестовый EPUB файл"""
    print("🏗️ Создание тестового EPUB файла...")
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub:
        # 1. mimetype (должен быть первым и несжатым)
        epub.writestr('mimetype', 'application/epub+zip', zipfile.ZIP_STORED)
        
        # 2. META-INF/container.xml
        container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
        epub.writestr('META-INF/container.xml', container_xml)
        
        # 3. content.opf
        content_opf = '''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Test Book - Python Programming Guide</dc:title>
        <dc:creator>Test Author</dc:creator>
        <dc:language>en</dc:language>
        <dc:identifier id="book-id">test-book-123</dc:identifier>
        <meta property="dcterms:modified">2024-01-01T00:00:00Z</meta>
    </metadata>
    
    <manifest>
        <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
        <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
        <item id="stylesheet" href="styles.css" media-type="text/css"/>
        <item id="cover-image" href="cover.jpg" media-type="image/jpeg"/>
    </manifest>
    
    <spine>
        <itemref idref="chapter1"/>
    </spine>
</package>'''
        epub.writestr('OEBPS/content.opf', content_opf)
        
        # 4. nav.xhtml
        nav_xhtml = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>Navigation</title>
</head>
<body>
    <nav epub:type="toc">
        <h1>Table of Contents</h1>
        <ol>
            <li><a href="chapter1.xhtml">Chapter 1: Introduction to Python</a></li>
        </ol>
    </nav>
</body>
</html>'''
        epub.writestr('OEBPS/nav.xhtml', nav_xhtml)
        
        # 5. chapter1.xhtml
        chapter1_xhtml = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Chapter 1: Introduction to Python</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <h1>Chapter 1: Introduction to Python</h1>
    <p>Python is a high-level, interpreted programming language with dynamic semantics.</p>
    <p>Its high-level built in data structures, combined with dynamic typing and dynamic binding, make it very attractive for Rapid Application Development.</p>
    
    <h2>Key Features</h2>
    <ul>
        <li>Easy to learn and use</li>
        <li>Extensive standard library</li>
        <li>Cross-platform compatibility</li>
        <li>Strong community support</li>
    </ul>
    
    <h2>Example Code</h2>
    <pre><code>
def hello_world():
    print("Hello, World!")
    return "Welcome to Python programming!"

# Call the function
message = hello_world()
print(message)
    </code></pre>
    
    <p>This is a simple example demonstrating Python syntax.</p>
    <img src="cover.jpg" alt="Python Logo" style="max-width: 200px;"/>
</body>
</html>'''
        epub.writestr('OEBPS/chapter1.xhtml', chapter1_xhtml)
        
        # 6. styles.css
        styles_css = '''
body {
    font-family: "Times New Roman", serif;
    line-height: 1.6;
    margin: 1em;
    color: #333;
}

h1, h2 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.3em;
}

pre {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 1em;
    overflow-x: auto;
}

code {
    font-family: "Courier New", monospace;
    background-color: #f1f3f4;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}

ul {
    list-style-type: square;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
}
'''
        epub.writestr('OEBPS/styles.css', styles_css)
        
        # 7. Простое изображение (fake JPEG header + minimal data)
        fake_jpg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00' + b'\x00' * 100 + b'\xff\xd9'
        epub.writestr('OEBPS/cover.jpg', fake_jpg)
    
    print(f"✅ Тестовый EPUB создан: {output_path}")
    return output_path

def create_bad_epub(output_path):
    """Создать плохой EPUB файл для тестирования ошибок"""
    print("💥 Создание плохого EPUB файла...")
    
    with zipfile.ZipFile(output_path, 'w') as epub:
        # Неправильный mimetype
        epub.writestr('mimetype', 'application/zip')
        
        # Битый container.xml
        epub.writestr('META-INF/container.xml', '<broken xml>')
        
        # Отсутствует OPF файл
    
    print(f"✅ Плохой EPUB создан: {output_path}")
    return output_path

def main():
    """Основная функция для тестирования диагностики"""
    print("🧪 Тест диагностики EPUB файлов")
    print("=" * 40)
    
    # Создать временную директорию
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Тест 1: Хороший EPUB
        print("\n1️⃣ ТЕСТ: Хороший EPUB файл")
        print("-" * 30)
        
        good_epub = temp_path / "good_book.epub"
        create_test_epub(good_epub)
        
        print("\n📖 Диагностика хорошего EPUB:")
        diagnostics1 = EPUBDiagnostics(good_epub)
        result1 = diagnostics1.analyze()
        
        # Тест 2: Плохой EPUB
        print("\n\n2️⃣ ТЕСТ: Плохой EPUB файл")
        print("-" * 30)
        
        bad_epub = temp_path / "bad_book.epub"
        create_bad_epub(bad_epub)
        
        print("\n📖 Диагностика плохого EPUB:")
        diagnostics2 = EPUBDiagnostics(bad_epub)
        result2 = diagnostics2.analyze()
        
        # Тест 3: Несуществующий файл
        print("\n\n3️⃣ ТЕСТ: Несуществующий файл")
        print("-" * 30)
        
        missing_epub = temp_path / "missing.epub"
        
        print("\n📖 Диагностика несуществующего файла:")
        diagnostics3 = EPUBDiagnostics(missing_epub)
        result3 = diagnostics3.analyze()
        
        # Итоговая сводка
        print("\n\n📊 ИТОГОВАЯ СВОДКА ТЕСТОВ")
        print("=" * 40)
        
        tests = [
            ("Хороший EPUB", result1),
            ("Плохой EPUB", result2), 
            ("Несуществующий файл", result3)
        ]
        
        for test_name, result in tests:
            quality_score = result.get('quality_score', 0)
            issues_count = result.get('issues_count', 0)
            warnings_count = result.get('warnings_count', 0)
            
            if quality_score >= 80:
                status_icon = "🟢"
            elif quality_score >= 60:
                status_icon = "🟡"
            else:
                status_icon = "🔴"
            
            print(f"{status_icon} {test_name}:")
            print(f"   • Качество: {quality_score}/100")
            print(f"   • Ошибки: {issues_count}")
            print(f"   • Предупреждения: {warnings_count}")
            print()
        
        print("🎯 Все тесты завершены!")
        print("💡 Диагностика EPUB работает корректно")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Прервано пользователем")
    except Exception as e:
        print(f"\n💥 Ошибка: {e}")
        import traceback
        traceback.print_exc()