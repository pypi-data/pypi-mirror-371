# onco-cola-utils

Мои общие утилиты для Python-проектов.

## Возможности

- `ReaderController` — работа с Excel-файлами
- Поддержка `local_id`, фильтрации, переименования
- Гибкое чтение и запись
- Интеграция с AI-ответами

## Установка

```bash
pip install onco-cola-utils
```

## Использование

```bash
from my_utils.reader_controller.core import ReaderController

rc = ReaderController(file_path="data.xlsx", file_output="out.xlsx")
rc.read_data()
print(rc.get_data())
```