"""Работа с датами для тестов календаря."""

from __future__ import annotations

import datetime as dt


def shift_months(date: dt.date, months: int, day: int) -> dt.date:
    """Дата с указанным днём через `months` месяцев от `date` (может быть < 0)."""
    index = date.year * 12 + (date.month - 1) + months
    return dt.date(index // 12, index % 12 + 1, day)
