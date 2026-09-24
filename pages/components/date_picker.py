"""Компонент всплывающего календаря (date picker) Jetpack Forms.

Календарь создаётся в конце <body> при фокусе на поле даты и удаляется
из DOM при закрытии. Структура:

* ``.dp`` — корень календаря;
* ``.dp-cal-month`` / ``.dp-cal-year`` — кнопки выбора месяца и года в шапке;
* ``.dp-prev`` / ``.dp-next`` — пагинация по месяцам;
* ``.dp-day`` — кнопки дней (42 шт.), ``.dp-edge-day`` — дни соседних месяцев,
  ``.dp-current`` — подсвеченный день, ``.dp-day-today`` — сегодняшний день;
* ``.dp-month[data-month]`` / ``.dp-year[data-year]`` — режимы выбора месяца / года.
"""

from __future__ import annotations

import datetime as dt

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BaseElement

# Названия месяцев так, как их выводит календарь сайта (не зависят от локали ОС).
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


class DatePicker(BaseElement):
    ROOT = (By.CSS_SELECTOR, ".dp")
    MONTH_BUTTON = (By.CSS_SELECTOR, ".dp .dp-cal-month")
    YEAR_BUTTON = (By.CSS_SELECTOR, ".dp .dp-cal-year")
    PREV_BUTTON = (By.CSS_SELECTOR, ".dp .dp-prev")
    NEXT_BUTTON = (By.CSS_SELECTOR, ".dp .dp-next")
    WEEKDAY_HEADERS = (By.CSS_SELECTOR, ".dp .dp-col-header")
    DAYS = (By.CSS_SELECTOR, ".dp .dp-day")
    DAYS_OF_SHOWN_MONTH = (By.CSS_SELECTOR, ".dp .dp-day:not(.dp-edge-day)")
    HIGHLIGHTED_DAY = (By.CSS_SELECTOR, ".dp .dp-day.dp-current")
    TODAY = (By.CSS_SELECTOR, ".dp .dp-day.dp-day-today")
    MONTHS_VIEW = (By.CSS_SELECTOR, ".dp .dp-months")
    YEARS_VIEW = (By.CSS_SELECTOR, ".dp .dp-years")

    # ---------- состояние ----------
    def is_opened(self) -> bool:
        return self.is_visible(self.ROOT)

    def wait_opened(self) -> None:
        self.find_visible(self.ROOT)

    def wait_closed(self) -> None:
        self.wait_invisible(self.ROOT)

    def shown_month(self) -> tuple[int, int]:
        """(год, месяц) страницы календаря, которая сейчас отображается."""
        month_name = self._text(self.MONTH_BUTTON)
        year = int(self._text(self.YEAR_BUTTON))
        return year, MONTHS.index(month_name) + 1

    def weekday_headers(self) -> list[str]:
        return [e.get_attribute("textContent").strip() for e in self.find_all(self.WEEKDAY_HEADERS)]

    def days_count(self) -> int:
        return len(self.find_all(self.DAYS))

    def highlighted_day(self) -> int:
        return int(self._text(self.HIGHLIGHTED_DAY))

    def today_day(self) -> int:
        return int(self._text(self.TODAY))

    # ---------- навигация ----------
    def next_month(self) -> None:
        self._paginate(self.NEXT_BUTTON, +1)

    def prev_month(self) -> None:
        self._paginate(self.PREV_BUTTON, -1)

    def go_to_month(self, year: int, month: int) -> None:
        """Листает календарь стрелками до нужного месяца (пагинация)."""
        with allure.step(f"Пролистать календарь до {MONTHS[month - 1]} {year}"):
            shown_year, shown_month = self.shown_month()
            diff = (year - shown_year) * 12 + (month - shown_month)
            for _ in range(abs(diff)):
                if diff > 0:
                    self.next_month()
                else:
                    self.prev_month()

    def select_day(self, day: int) -> None:
        with allure.step(f"Кликнуть по дню {day}"):
            for button in self.find_all(self.DAYS_OF_SHOWN_MONTH):
                if button.get_attribute("textContent").strip() == str(day):
                    button.click()
                    break
            else:
                raise AssertionError(f"В календаре нет дня {day}")
            self.wait_closed()

    def select_date(self, date: dt.date) -> None:
        """Выбор даты пагинацией по месяцам — рекомендованный на сайте способ."""
        with allure.step(f"Выбрать в календаре дату {date.isoformat()} (пагинация)"):
            self.go_to_month(date.year, date.month)
            self.select_day(date.day)

    def select_date_via_dropdowns(self, date: dt.date) -> None:
        """Выбор даты через выпадающие списки года и месяца в шапке календаря."""
        with allure.step(f"Выбрать дату {date.isoformat()} через списки года и месяца"):
            with allure.step(f"Открыть список лет и выбрать {date.year}"):
                self.click(self.YEAR_BUTTON)
                self.find_visible(self.YEARS_VIEW)
                self.click((By.CSS_SELECTOR, f".dp .dp-year[data-year='{date.year}']"))
            with allure.step(f"Открыть список месяцев и выбрать {MONTHS[date.month - 1]}"):
                self.click(self.MONTH_BUTTON)
                self.find_visible(self.MONTHS_VIEW)
                self.click((By.CSS_SELECTOR, f".dp .dp-month[data-month='{date.month - 1}']"))
            self.wait().until(lambda _: self.shown_month() == (date.year, date.month))
            self.select_day(date.day)

    # ---------- внутреннее ----------
    def _paginate(self, button, step: int) -> None:
        year, month = self.shown_month()
        month_index = year * 12 + (month - 1) + step
        expected = (month_index // 12, month_index % 12 + 1)
        self.click(button)
        self.wait().until(
            lambda _: self.shown_month() == expected,
            message=f"Календарь не перелистнулся на {expected}",
        )

    def _text(self, locator) -> str:
        # textContent не зависит от CSS text-transform, в отличие от .text
        return self.find_visible(locator).get_attribute("textContent").strip()
