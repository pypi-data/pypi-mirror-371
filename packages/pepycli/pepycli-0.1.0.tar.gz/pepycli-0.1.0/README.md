# PepyCLI

**PepyCLI** — это удобный CLI-инструмент для работы с [Pepy.tech API](https://pepy.tech/), который предоставляет статистику загрузок Python-пакетов прямо из терминала.

---

## Установка

Через `pip`:

```bash
pip install pepycli
```

---

## Использование

Посмотреть доступные команды:

```bash
pepycli --help
```

### Получить аналитику по проекту
```bash
pepycli analytics marzban-client
```

Пример вывода:
```python
{
  'id': 'marzban-client',
  'total_downloads': 229,
  'versions': ['0.1.0', '0.1.1'],
  'downloads': {
    '2025-08-19': {'0.1.1': 108, '0.1.0': 51},
    '2025-08-20': {'0.1.1': 65, '0.1.0': 5}
  }
}
```

### Получить общее количество загрузок проекта
```bash
pepycli downloads fastapi
```

Пример вывода:
```bash
{
  "downloads": {
    "2023-08-29": {
      "1.0": 10
    }
  }
}
```

