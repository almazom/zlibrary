# 🔐 Setting Up Z-Library Credentials

Для работы с Z-Library API необходимы учетные данные аккаунта Z-Library. Этот гайд покажет, как безопасно настроить credentials.

## 🚨 **Важно: Безопасность**

**НИКОГДА** не коммитьте настоящие credentials в git! Всегда используйте `.env` файл, который исключен из git через `.gitignore`.

## 📝 **Шаг 1: Создание аккаунта Z-Library**

1. **Перейдите на сайт**: https://z-library.sk
2. **Зарегистрируйтесь** или войдите в существующий аккаунт
3. **Важно**: Нужен аккаунт типа "singlelogin" для API доступа

## 🔧 **Шаг 2: Настройка Credentials**

### Вариант A: Автоматическая настройка (рекомендуется)

```bash
# Запустите тест - он предложит создать .env файл автоматически
./run_download_test.sh
```

### Вариант B: Ручная настройка

1. **Скопируйте шаблон**:
   ```bash
   cp env.template .env
   ```

2. **Отредактируйте `.env` файл**:
   ```bash
   nano .env
   # или используйте любой другой редактор
   ```

3. **Заполните ваши credentials**:
   ```env
   # Z-Library account credentials
   ZLOGIN=your-email@example.com
   ZPASSW=your-password-here
   ```

## 🛡️ **Структура `.env` файла**

```env
# Z-Library account credentials (ОБЯЗАТЕЛЬНО)
ZLOGIN=your-email@example.com
ZPASSW=your-password-here

# Optional: Proxy settings (если нужен прокси)
# PROXY_HTTP=http://proxy.example.com:8080
# PROXY_SOCKS5=socks5://127.0.0.1:9050

# Optional: Debug settings (для отладки)
# ZLIBRARY_DEBUG=true
# ZLIBRARY_LOG_LEVEL=DEBUG
```

## 🔍 **Проверка настройки**

После создания `.env` файла запустите тест:

```bash
./run_download_test.sh
```

Если credentials настроены правильно, вы увидите:
```
🔧 Loaded environment variables from /path/to/project/.env
🔐 Logging in...
✅ Login successful!
```

## ⚠️ **Безопасность и Best Practices**

### ✅ **Что НУЖНО делать:**
- ✅ Всегда используйте `.env` файл для хранения credentials
- ✅ Убедитесь, что `.env` есть в `.gitignore` (уже настроено)
- ✅ Используйте сильные пароли для аккаунта Z-Library
- ✅ Регулярно меняйте пароли

### ❌ **Что НЕ НУЖНО делать:**
- ❌ НЕ коммитьте `.env` файл в git
- ❌ НЕ храните credentials в коде
- ❌ НЕ делитесь своими credentials с другими
- ❌ НЕ используйте production credentials для тестирования

## 🔄 **Альтернативные способы настройки**

### Environment Variables
```bash
export ZLOGIN="your-email@example.com"
export ZPASSW="your-password"
./run_download_test.sh
```

### Docker / CI Environment
```yaml
environment:
  ZLOGIN: your-email@example.com
  ZPASSW: your-password
```

## 🚨 **Troubleshooting**

### Ошибка: "❌ Login failed"
- Проверьте правильность email и пароля
- Убедитесь, что аккаунт активен
- Проверьте, что у вас есть интернет соединение

### Ошибка: "❌ Z-Library credentials not found!"
- Убедитесь, что `.env` файл существует
- Проверьте, что в `.env` файле правильно заполнены `ZLOGIN` и `ZPASSW`
- Убедитесь, что нет лишних пробелов в credentials

### Ошибка: "No working domains have been found"
- Возможно, Z-Library временно недоступен
- Попробуйте использовать прокси или VPN
- Попробуйте позже

## 📊 **Лимиты скачивания**

Z-Library имеет дневные лимиты скачивания:
- **Стандартный аккаунт**: обычно 5-10 книг в день
- **Premium аккаунт**: больше лимиты

Проверить текущие лимиты можно в тесте:
```python
limits = await lib.profile.get_limits()
print(f"Remaining downloads: {limits['daily_remaining']}")
```

## 🎯 **Готово!**

После настройки credentials вы можете:
- 🧪 Запускать интеграционные тесты
- 📚 Использовать API для поиска и скачивания книг
- 🔍 Экспериментировать с различными функциями библиотеки

---
*💡 Помните: Используйте API ответственно и уважайте лимиты сервиса!* 