# XTools-py

![PyPI](https://img.shields.io/pypi/v/xtools?color=blue&label=PyPI) ![Python](https://img.shields.io/badge/Python-%3E%3D3.7-blue) ![License](https://img.shields.io/github/license/SikWeet/xtools)

**XTools-py** — это мощная библиотека с полезными утилитами для Python-разработчиков, предназначенная для упрощения рутинных задач. Включает в себя инструменты для работы с конфигурационными файлами, матрицами, валидацией данных, кешированием, поиском информации и многим другим.

## 🚀 Установка

Установить библиотеку можно через `pip`:

```sh
pip install xtools-py
```

## 📌 Возможности

- **Поиск данных** (`Find`) — быстрый поиск в структурах данных.
- **Работа с матрицами** (`Matrix`) — удобные операции с матрицами.
- **Конфигурационные файлы** (`Config`) — работа с JSON, YAML и INI файлами.
- **Валидация данных** (`Validator`) — проверка строк, чисел и других типов данных.
- **Кеширование** (`Cache`) — простой и эффективный кеш.
- **Работа с датами и временем** (`DateTimeUtils`) — удобные функции для работы с датами.
- **Математические функции** (`MathUtils`) — расширенные математические операции.
- **Работа с цветами** (`ColorUtils`) — преобразование и обработка цветов.
- **Шифрование** (`Encryption`) — базовые функции шифрования и хеширования.
- **Работа с текстом** (`TextUtils`) — удобные текстовые манипуляции.
- **Конвертация единиц измерения** (`Unit`) — перевод величин между разными системами.
- **Облачное хранилище** (`AWS S3`) — удобное взаимодействие с облачным хранилищем (асинхронно/синхронно).

## 📖 Использование

### 1. Работа с конфигурацией

```python
from xtools import Config

config = Config("config.json")
config.set("app.debug", True)
config.save()
```

### 2. Поиск данных

```python
from xtools import Find

data = ["apple", "banana", "cherry"]
result = Find.get_max(data)  # banana

numbers = [123, 321, 213]
result = Find.get_max(numbers) # 321

# Работа с словарём:

data = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
    {"name": "Charlie", "age": 25}
]

results = Find.by_key_value(data, "age", 25) # [{'name': 'Alice', 'age': 25}, {'name': 'Charlie', 'age': 25}]

results = Find.contains(data, "name", "Al") # [{'name': 'Alice', 'age': 25}]
```

### 3. Работа с кешем

```python
from xtools import Cache

cache = Cache()
cache.set("key", "value", ttl=60)  # Хранится 60 секунд
print(cache.get("key"))  # value
```

### 4. Работа с датами

```python
from xtools.utils import DateTimeUtils

print(DateTimeUtils.current_timestamp())
print(DateTimeUtils.format_date("2025-02-08", "%d.%m.%Y"))
```

### 5. Работа с цветами

```python
from xtools.utils import ColorUtils

print(ColorUtils.hex_to_rgb("#FFFFFF"))  # (255, 255, 255)
print(ColorUtils.rgb_to_hex(255, 255, 255))  # #FFFFFF

```

### 6. Конвертация единиц измерения

```python
from xtools import UnitConverter

print(UnitConverter.celsius_to_fahrenheit(25))  # 77.0
print(UnitConverter.meters_to_kilometers(1000))  # 1.0
```

### 7. Шифрование и дешифрование

```python
from xtools import EncryptionUtils

key = EncryptionUtils.generate_key()
encrypted = EncryptionUtils.encrypt("Hello, World!", key)
decrypted = EncryptionUtils.decrypt(encrypted, key)

print(encrypted)
print(decrypted)  # Hello, World!
```

### 8. Работа с AWS S3 (синхронно)
```python
from xtools.storage import S3Storage

s3 = S3Storage("my-bucket", "ACCESS_KEY", "SECRET_KEY")

# Загрузка файла
s3.upload_file("local.txt", "remote.txt")

# Список файлов
print(s3.list_files())
```

### 9. Работа с AWS S3 (асинхронно)
```python
import asyncio
from xtools.storage import AsyncS3Storage

async def main():
    s3 = AsyncS3Storage("my-bucket", "ACCESS_KEY", "SECRET_KEY")
    await s3.upload_file("local.txt", "remote.txt")
    print(await s3.list_files())

asyncio.run(main())
```

## 💡 Roadmap

- Добавление поддержки **Redis** для кеша
- Расширенные возможности валидации
- Улучшенные математические функции

## 📜 Лицензия

Проект распространяется под лицензией **MIT**.

## 🤝 Контрибьютинг

Если у вас есть идеи для улучшения библиотеки, создайте **issue** или **pull request** на [GitHub](https://github.com/SikWeet/xtools).

## 🔗 Связь

- 📧 Email: girectx@gmail.com
- 💻 GitHub: [SikWeet](https://github.com/SikWeet)

---

📌 **XTools-py** — инструменты, которые делают разработку проще! 🚀

