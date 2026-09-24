"""Тесты страницы «Calendars» — https://practice-automation.com/calendars/"""

from __future__ import annotations

import datetime as dt

import allure
import pytest

from pages.calendar_page import CalendarPage
from pages.components.jetpack_form import SUCCESS_TITLE
from utils.dates import shift_months

INVALID_DATE_ERROR = "Please enter a valid date."
SUMMARY_LABEL = "Select or enter a date"

pytestmark = [allure.epic("UI practice-automation.com"), allure.feature("Календарь")]


@allure.story("Позитивные сценарии")
@pytest.mark.positive
class TestCalendarPositive:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-CAL-01. Страница календаря отображает поле даты с подсказкой формата")
    def test_page_elements(self, calendar_page: CalendarPage):
        with allure.step("Проверить заголовок, подпись поля, подсказку формата и кнопку"):
            assert calendar_page.heading == "Calendars"
            assert calendar_page.date_label == "Select or enter a date"
            assert calendar_page.date_format_hint == "YYYY-MM-DD"
            assert calendar_page.date_value == "", "Поле даты должно быть пустым"
            assert calendar_page.form.is_submit_button_displayed()
            assert not calendar_page.date_picker.is_opened(), "Календарь не должен быть открыт сразу"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-CAL-02. Календарь открывается на текущем месяце с подсветкой сегодняшней даты")
    def test_date_picker_opens_on_current_month(self, calendar_page: CalendarPage):
        today = dt.date.today()
        picker = calendar_page.open_date_picker()
        with allure.step("Проверить месяц, год, сетку дней и сегодняшний день"):
            assert picker.shown_month() == (today.year, today.month)
            assert picker.weekday_headers() == ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
            assert picker.days_count() == 42, "Сетка календаря — 6 недель по 7 дней"
            assert picker.today_day() == today.day
            assert picker.highlighted_day() == today.day

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-CAL-03. Выбор сегодняшней даты кликом в календаре")
    def test_select_today(self, calendar_page: CalendarPage):
        today = dt.date.today()
        calendar_page.select_date(today)
        with allure.step("Проверить значение поля и то, что календарь закрылся"):
            assert calendar_page.date_value == today.isoformat()
            assert not calendar_page.date_picker.is_opened()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-CAL-04. Пагинация календаря: переход на следующий и предыдущий месяц")
    def test_month_pagination(self, calendar_page: CalendarPage):
        today = dt.date.today()
        picker = calendar_page.open_date_picker()
        next_month = shift_months(today, 1, 1)
        prev_month = shift_months(today, -1, 1)

        with allure.step("Нажать «Next Month»"):
            picker.next_month()
            assert picker.shown_month() == (next_month.year, next_month.month)
        with allure.step("Дважды нажать «Previous Month»"):
            picker.prev_month()
            picker.prev_month()
            assert picker.shown_month() == (prev_month.year, prev_month.month)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-CAL-05. Выбор даты пагинацией: {case}")
    @pytest.mark.parametrize(
        ("case", "months", "day"),
        [
            ("дата в будущем (+3 месяца)", 3, 15),
            ("дата в прошлом (−14 месяцев)", -14, 28),
        ],
        ids=["future", "past"],
    )
    def test_select_date_with_pagination(
        self, calendar_page: CalendarPage, case: str, months: int, day: int
    ):
        target = shift_months(dt.date.today(), months, day)
        calendar_page.select_date(target)
        with allure.step(f"Проверить, что в поле подставилась дата {target.isoformat()}"):
            assert calendar_page.date_value == target.isoformat()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-CAL-06. Выбор даты через выпадающие списки года и месяца")
    def test_select_date_via_year_and_month_dropdowns(self, calendar_page: CalendarPage):
        target = dt.date(2000, 1, 1)
        calendar_page.select_date_via_dropdowns(target)
        with allure.step("Проверить значение поля"):
            assert calendar_page.date_value == "2000-01-01"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-CAL-07. Выбор даты с клавиатуры (стрелки и Enter)")
    def test_select_date_with_keyboard(self, calendar_page: CalendarPage):
        tomorrow = dt.date.today() + dt.timedelta(days=1)
        calendar_page.select_tomorrow_with_keyboard()
        with allure.step("Проверить, что выбран завтрашний день"):
            assert calendar_page.date_value == tomorrow.isoformat()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-CAL-08. Введённая вручную дата подсвечивается в календаре")
    def test_typed_date_is_highlighted_in_picker(self, calendar_page: CalendarPage):
        calendar_page.enter_date("2030-05-17")
        picker = calendar_page.date_picker
        with allure.step("Проверить, что календарь перешёл на май 2030 и подсветил 17 число"):
            picker.wait().until(lambda _: picker.shown_month() == (2030, 5))
            assert picker.highlighted_day() == 17

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("TC-CAL-09. Отправка даты, выбранной в календаре, и возврат к форме")
    def test_submit_date_selected_in_picker(self, calendar_page: CalendarPage):
        target = shift_months(dt.date.today(), 1, 10)
        calendar_page.select_date(target)
        calendar_page.form.submit()
        calendar_page.form.wait_success()
        with allure.step("Проверить сообщение об успехе и отправленную дату"):
            assert calendar_page.form.success_title == SUCCESS_TITLE
            assert calendar_page.form.submitted_values() == {SUMMARY_LABEL: target.isoformat()}
        calendar_page.form.go_back()
        with allure.step("Проверить, что снова отображается пустая форма"):
            assert calendar_page.date_value == ""
            assert calendar_page.form.is_submit_button_displayed()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-CAL-10. Отправка корректной даты, введённой вручную (29 февраля високосного года)")
    def test_submit_manually_entered_date(self, calendar_page: CalendarPage):
        calendar_page.submit_date("2024-02-29")
        calendar_page.form.wait_success()
        with allure.step("Проверить сообщение об успехе и отправленную дату"):
            assert calendar_page.form.success_title == SUCCESS_TITLE
            assert calendar_page.form.submitted_values() == {SUMMARY_LABEL: "2024-02-29"}


@allure.story("Негативные сценарии")
@pytest.mark.negative
class TestCalendarNegative:
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-CAL-N1. Отправка формы с пустой датой не выполняется")
    def test_submit_empty_date(self, calendar_page: CalendarPage):
        calendar_page.form.submit()
        with allure.step("Проверить, что форма не отправлена"):
            assert calendar_page.form.success_not_displayed_within(5)
            assert calendar_page.form.is_submit_button_displayed()
            assert calendar_page.date_value == ""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-CAL-{case_id}. Некорректная дата «{value}» не принимается: {reason}")
    @pytest.mark.parametrize(
        ("case_id", "value", "reason"),
        [
            ("N2", "2026-13-45", "несуществующие месяц и день"),
            ("N3", "2023-02-29", "29 февраля в невисокосном году"),
            ("N4", "15/10/2026", "формат ДД/ММ/ГГГГ вместо ГГГГ-ММ-ДД"),
            ("N5", "abcdef", "буквы вместо даты"),
        ],
        ids=["impossible-date", "non-leap-feb-29", "wrong-format", "letters"],
    )
    def test_invalid_date_is_rejected(
        self, calendar_page: CalendarPage, case_id: str, value: str, reason: str
    ):
        calendar_page.submit_date(value)
        field = calendar_page.date_input
        error = calendar_page.form.wait_field_error(field)
        with allure.step("Проверить сообщение об ошибке и то, что форма не отправлена"):
            assert error == INVALID_DATE_ERROR
            assert calendar_page.form.is_marked_invalid(field), "Поле должно быть помечено aria-invalid"
            assert not calendar_page.form.is_success_displayed()
            assert calendar_page.date_value == value, "Введённое значение не должно сбрасываться"
