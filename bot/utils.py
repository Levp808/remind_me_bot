from datetime import datetime


# Преобразование строки в datetime
def parse_datetime(s: str) -> datetime | None:
    try:
        # Попробовать встроенный ISO‑парсер (Python 3.7+)
        # поддерживает “YYYY-MM-DDTHH:MM:SS[.ffffff][+HH:MM]”
        return datetime.fromisoformat(s)
    except ValueError:
        return None

# Преобразование datetime в строку
def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

# Проверка, что дата в будущем
def is_future_datetime(dt: datetime) -> bool:
    return dt > datetime.now()


