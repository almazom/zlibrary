#!/usr/bin/env python3
"""
📖 EPUB Diagnostics Tool
Анализирует качество загруженного EPUB файла
"""

import zipfile
import xml.etree.ElementTree as ET
import os
import sys
from pathlib import Path
import mimetypes
from collections import defaultdict
import re

class EPUBDiagnostics:
    def __init__(self, epub_path):
        self.epub_path = Path(epub_path)
        self.issues = []
        self.warnings = []
        self.info = {}
        
    def analyze(self):
        """Полный анализ EPUB файла"""
        print(f"📖 Анализ EPUB: {self.epub_path.name}")
        print("=" * 50)
        
        if not self.epub_path.exists():
            self.issues.append(f"Файл не найден: {self.epub_path}")
            return self.generate_report()
        
        if not self.epub_path.suffix.lower() == '.epub':
            self.warnings.append("Файл не имеет расширение .epub")
        
        try:
            # Основные проверки
            self._check_file_structure()
            self._check_mimetype()
            self._check_container_xml()
            self._check_opf_file()
            self._check_content_files()
            self._check_images()
            self._analyze_size_and_stats()
            
        except Exception as e:
            self.issues.append(f"Критическая ошибка анализа: {e}")
        
        return self.generate_report()
    
    def _check_file_structure(self):
        """Проверка базовой структуры ZIP"""
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as zip_file:
                self.file_list = zip_file.namelist()
                self.info['total_files'] = len(self.file_list)
                
                # Проверка обязательных файлов
                required_files = ['mimetype', 'META-INF/container.xml']
                
                for req_file in required_files:
                    if req_file not in self.file_list:
                        self.issues.append(f"Отсутствует обязательный файл: {req_file}")
                
                # Проверка целостности ZIP
                bad_files = zip_file.testzip()
                if bad_files:
                    self.issues.append(f"Поврежденные файлы в архиве: {bad_files}")
                
                print(f"✅ ZIP структура: {len(self.file_list)} файлов")
                
        except zipfile.BadZipFile:
            self.issues.append("Файл не является корректным ZIP архивом")
        except Exception as e:
            self.issues.append(f"Ошибка чтения файла: {e}")
    
    def _check_mimetype(self):
        """Проверка файла mimetype"""
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as zip_file:
                if 'mimetype' in self.file_list:
                    mimetype_content = zip_file.read('mimetype').decode('utf-8').strip()
                    
                    if mimetype_content == 'application/epub+zip':
                        print("✅ MIME type: корректный")
                    else:
                        self.issues.append(f"Неверный MIME type: {mimetype_content}")
                else:
                    self.issues.append("Отсутствует файл mimetype")
        except Exception as e:
            self.issues.append(f"Ошибка проверки mimetype: {e}")
    
    def _check_container_xml(self):
        """Проверка META-INF/container.xml"""
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as zip_file:
                if 'META-INF/container.xml' in self.file_list:
                    container_content = zip_file.read('META-INF/container.xml')
                    
                    # Парсинг XML
                    root = ET.fromstring(container_content)
                    
                    # Найти OPF файл
                    ns = {'container': 'urn:oasis:names:tc:opendocument:xmlns:container'}
                    rootfiles = root.findall('.//container:rootfile', ns)
                    
                    if rootfiles:
                        self.opf_path = rootfiles[0].get('full-path')
                        print(f"✅ Container.xml: OPF файл - {self.opf_path}")
                    else:
                        self.issues.append("Не найден путь к OPF файлу в container.xml")
                        
                else:
                    self.issues.append("Отсутствует META-INF/container.xml")
        except ET.ParseError as e:
            self.issues.append(f"Ошибка парсинга container.xml: {e}")
        except Exception as e:
            self.issues.append(f"Ошибка проверки container.xml: {e}")
    
    def _check_opf_file(self):
        """Проверка OPF файла (метаданные и структура)"""
        if not hasattr(self, 'opf_path'):
            return
        
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as zip_file:
                if self.opf_path in self.file_list:
                    opf_content = zip_file.read(self.opf_path)
                    
                    # Парсинг OPF
                    root = ET.fromstring(opf_content)
                    
                    # Извлечь метаданные
                    self._extract_metadata(root)
                    
                    # Проверить манифест
                    self._check_manifest(root)
                    
                    # Проверить spine
                    self._check_spine(root)
                    
                    print("✅ OPF файл: структура корректна")
                    
                else:
                    self.issues.append(f"OPF файл не найден: {self.opf_path}")
                    
        except ET.ParseError as e:
            self.issues.append(f"Ошибка парсинга OPF файла: {e}")
        except Exception as e:
            self.issues.append(f"Ошибка проверки OPF файла: {e}")
    
    def _extract_metadata(self, opf_root):
        """Извлечение метаданных из OPF"""
        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        metadata = opf_root.find('.//opf:metadata', ns)
        if metadata is not None:
            # Основные метаданные
            title = metadata.find('.//dc:title', ns)
            creator = metadata.find('.//dc:creator', ns)
            language = metadata.find('.//dc:language', ns)
            identifier = metadata.find('.//dc:identifier', ns)
            
            self.info['title'] = title.text if title is not None else "Не указано"
            self.info['creator'] = creator.text if creator is not None else "Не указано"
            self.info['language'] = language.text if language is not None else "Не указано"
            self.info['identifier'] = identifier.text if identifier is not None else "Не указано"
            
            print(f"📚 Название: {self.info['title']}")
            print(f"👤 Автор: {self.info['creator']}")
            print(f"🌍 Язык: {self.info['language']}")
            
        else:
            self.warnings.append("Метаданные не найдены в OPF файле")
    
    def _check_manifest(self, opf_root):
        """Проверка манифеста (список всех файлов)"""
        ns = {'opf': 'http://www.idpf.org/2007/opf'}
        
        manifest = opf_root.find('.//opf:manifest', ns)
        if manifest is not None:
            items = manifest.findall('.//opf:item', ns)
            
            self.manifest_files = {}
            self.info['manifest_items'] = len(items)
            
            file_types = defaultdict(int)
            
            for item in items:
                href = item.get('href', '')
                media_type = item.get('media-type', '')
                item_id = item.get('id', '')
                
                self.manifest_files[item_id] = {
                    'href': href,
                    'media_type': media_type
                }
                
                # Счетчик типов файлов
                if 'html' in media_type or 'xhtml' in media_type:
                    file_types['HTML/XHTML'] += 1
                elif 'image' in media_type:
                    file_types['Images'] += 1
                elif 'css' in media_type:
                    file_types['CSS'] += 1
                else:
                    file_types['Other'] += 1
            
            print(f"📋 Манифест: {len(items)} элементов")
            for file_type, count in file_types.items():
                print(f"   • {file_type}: {count}")
            
        else:
            self.issues.append("Манифест не найден в OPF файле")
    
    def _check_spine(self, opf_root):
        """Проверка spine (порядок чтения)"""
        ns = {'opf': 'http://www.idpf.org/2007/opf'}
        
        spine = opf_root.find('.//opf:spine', ns)
        if spine is not None:
            itemrefs = spine.findall('.//opf:itemref', ns)
            
            self.info['spine_items'] = len(itemrefs)
            print(f"📖 Spine: {len(itemrefs)} глав")
            
            # Проверить, что все itemref ссылаются на существующие элементы манифеста
            if hasattr(self, 'manifest_files'):
                for itemref in itemrefs:
                    idref = itemref.get('idref', '')
                    if idref not in self.manifest_files:
                        self.issues.append(f"Spine ссылается на несуществующий элемент: {idref}")
            
        else:
            self.issues.append("Spine не найден в OPF файле")
    
    def _check_content_files(self):
        """Проверка содержимого файлов"""
        if not hasattr(self, 'manifest_files'):
            return
        
        html_files = 0
        css_files = 0
        total_content_size = 0
        
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as zip_file:
                for item_id, item_info in self.manifest_files.items():
                    href = item_info['href']
                    media_type = item_info['media_type']
                    
                    # Построить полный путь с учетом базовой директории OPF
                    opf_dir = str(Path(self.opf_path).parent)
                    if opf_dir == '.':
                        full_path = href
                    else:
                        full_path = f"{opf_dir}/{href}"
                    
                    # Проверить существование файла
                    if full_path in self.file_list:
                        file_info = zip_file.getinfo(full_path)
                        total_content_size += file_info.file_size
                        
                        # Проверить HTML/XHTML файлы
                        if 'html' in media_type or 'xhtml' in media_type:
                            html_files += 1
                            self._check_html_file(zip_file, full_path)
                        
                        # Проверить CSS файлы  
                        elif 'css' in media_type:
                            css_files += 1
                    else:
                        self.issues.append(f"Файл из манифеста не найден: {full_path}")
            
            self.info['html_files'] = html_files
            self.info['css_files'] = css_files
            self.info['content_size'] = total_content_size
            
            print(f"📄 Контент: {html_files} HTML, {css_files} CSS")
            print(f"💾 Размер контента: {total_content_size:,} байт")
            
        except Exception as e:
            self.warnings.append(f"Ошибка проверки контента: {e}")
    
    def _check_html_file(self, zip_file, file_path):
        """Базовая проверка HTML файла"""
        try:
            content = zip_file.read(file_path).decode('utf-8', errors='ignore')
            
            # Простые проверки
            if len(content.strip()) == 0:
                self.warnings.append(f"Пустой HTML файл: {file_path}")
            
            # Проверка на наличие базовых HTML тегов
            if '<html' not in content.lower() and '<body' not in content.lower():
                self.warnings.append(f"Возможно некорректный HTML: {file_path}")
                
        except Exception as e:
            self.warnings.append(f"Ошибка чтения HTML файла {file_path}: {e}")
    
    def _check_images(self):
        """Проверка изображений"""
        if not hasattr(self, 'manifest_files'):
            return
        
        image_count = 0
        image_size = 0
        image_types = defaultdict(int)
        
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as zip_file:
                for item_id, item_info in self.manifest_files.items():
                    media_type = item_info['media_type']
                    
                    if 'image' in media_type:
                        href = item_info['href']
                        opf_dir = str(Path(self.opf_path).parent)
                        
                        if opf_dir == '.':
                            full_path = href
                        else:
                            full_path = f"{opf_dir}/{href}"
                        
                        if full_path in self.file_list:
                            file_info = zip_file.getinfo(full_path)
                            image_count += 1
                            image_size += file_info.file_size
                            
                            # Определить тип изображения
                            ext = Path(href).suffix.lower()
                            image_types[ext] += 1
                        else:
                            self.warnings.append(f"Изображение не найдено: {full_path}")
            
            self.info['image_count'] = image_count
            self.info['image_size'] = image_size
            
            if image_count > 0:
                print(f"🖼️ Изображения: {image_count} файлов ({image_size:,} байт)")
                for img_type, count in image_types.items():
                    print(f"   • {img_type}: {count}")
            else:
                print("🖼️ Изображения: не найдены")
                
        except Exception as e:
            self.warnings.append(f"Ошибка проверки изображений: {e}")
    
    def _analyze_size_and_stats(self):
        """Анализ размера и статистики"""
        file_size = self.epub_path.stat().st_size
        self.info['file_size'] = file_size
        
        # Рассчитать степень сжатия
        if hasattr(self, 'info') and 'content_size' in self.info:
            compression_ratio = (1 - file_size / max(self.info['content_size'], 1)) * 100
            self.info['compression_ratio'] = compression_ratio
        
        print(f"📊 Размер файла: {file_size:,} байт ({file_size/1024/1024:.1f} MB)")
        
        # Оценка качества
        self._assess_quality()
    
    def _assess_quality(self):
        """Оценка общего качества EPUB"""
        score = 100
        quality_issues = []
        
        # Снижение за критические ошибки
        critical_issues = len(self.issues)
        score -= critical_issues * 20
        
        # Снижение за предупреждения
        warning_count = len(self.warnings)
        score -= warning_count * 5
        
        # Проверки качества
        if self.info.get('file_size', 0) < 1024:  # Меньше 1KB
            score -= 30
            quality_issues.append("Подозрительно маленький размер файла")
        
        if self.info.get('html_files', 0) == 0:
            score -= 25
            quality_issues.append("Отсутствуют HTML файлы с контентом")
        
        if not self.info.get('title') or self.info.get('title') == "Не указано":
            score -= 10
            quality_issues.append("Отсутствует название книги")
        
        if not self.info.get('creator') or self.info.get('creator') == "Не указано":
            score -= 10
            quality_issues.append("Отсутствует автор")
        
        # Ограничить оценку
        score = max(0, min(100, score))
        
        self.info['quality_score'] = score
        self.info['quality_issues'] = quality_issues
        
        print(f"📈 Оценка качества: {score}/100")
    
    def generate_report(self):
        """Генерация итогового отчета"""
        print("\n" + "="*50)
        print("📋 ИТОГОВЫЙ ОТЧЕТ")
        print("="*50)
        
        # Основная информация
        if self.info:
            print("\n📚 МЕТАДАННЫЕ:")
            for key, value in self.info.items():
                if key.startswith('quality_'):
                    continue
                print(f"   • {key}: {value}")
        
        # Оценка качества
        quality_score = self.info.get('quality_score', 0)
        if quality_score >= 80:
            quality_status = "🟢 ОТЛИЧНОЕ"
        elif quality_score >= 60:
            quality_status = "🟡 ХОРОШЕЕ"
        elif quality_score >= 40:
            quality_status = "🟠 УДОВЛЕТВОРИТЕЛЬНОЕ"
        else:
            quality_status = "🔴 ПЛОХОЕ"
        
        print(f"\n🎯 КАЧЕСТВО EPUB: {quality_status} ({quality_score}/100)")
        
        # Критические ошибки
        if self.issues:
            print(f"\n❌ КРИТИЧЕСКИЕ ОШИБКИ ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   • {issue}")
        
        # Предупреждения
        if self.warnings:
            print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЯ ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # Проблемы качества
        quality_issues = self.info.get('quality_issues', [])
        if quality_issues:
            print(f"\n📉 ПРОБЛЕМЫ КАЧЕСТВА:")
            for issue in quality_issues:
                print(f"   • {issue}")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if quality_score >= 80:
            print("   ✅ EPUB файл высокого качества, готов к использованию")
        elif self.issues:
            print("   🔧 Требуется исправление критических ошибок")
            print("   📖 Файл может не открываться в некоторых читалках")
        elif quality_score < 60:
            print("   ⚠️ Рекомендуется найти версию лучшего качества")
            print("   📱 Возможны проблемы при чтении на устройствах")
        else:
            print("   👍 Файл пригоден для чтения с небольшими недочетами")
        
        print("\n" + "="*50)
        
        return {
            'quality_score': quality_score,
            'status': quality_status,
            'issues_count': len(self.issues),
            'warnings_count': len(self.warnings),
            'info': self.info,
            'issues': self.issues,
            'warnings': self.warnings
        }

def main():
    """Основная функция для диагностики EPUB"""
    if len(sys.argv) != 2:
        print("Использование: python epub_diagnostics.py <путь_к_epub_файлу>")
        return 1
    
    epub_path = sys.argv[1]
    
    # Создать диагностик и запустить анализ
    diagnostics = EPUBDiagnostics(epub_path)
    result = diagnostics.analyze()
    
    # Вернуть код выхода на основе качества
    quality_score = result['quality_score']
    if quality_score >= 80:
        return 0  # Отличное качество
    elif quality_score >= 60:
        return 0  # Хорошее качество 
    elif result['issues_count'] > 0:
        return 2  # Есть критические ошибки
    else:
        return 1  # Низкое качество

if __name__ == "__main__":
    sys.exit(main())