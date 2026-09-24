"""Тесты страницы с формой «Form Fields» — https://practice-automation.com/form-fields/

Здесь реализован п.5 задания: поле Message заполняется списком элементов
из раздела «Automation tools», полученным средствами Selenium.
"""

from __future__ import annotations

import allure
import pytest

from pages.form_fields_page import SUCCESS_ALERT_TEXT, FormFieldsPage

EXPECTED_TOOLS = ["Selenium", "Playwright", "Cypress", "Appium", "Katalon Studio"]

pytestmark = [allure.epic("UI practice-automation.com"), allure.feature("Форма (Form Fields)")]


@allure.story("Позитивные сценарии")
@pytest.mark.positive
class TestFormFieldsPositive:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-FF-01. Раздел «Automation tools» содержит ожидаемый список инструментов")
    def test_automation_tools_list(self, form_fields_page: FormFieldsPage):
        tools = form_fields_page.automation_tools()
        with allure.step("Сравнить список с ожидаемым"):
            assert tools == EXPECTED_TOOLS

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("TC-FF-02. Поле Message заполняется списком из «Automation tools» через запятую")
    def test_message_filled_with_automation_tools(self, form_fields_page: FormFieldsPage):
        expected = ", ".join(form_fields_page.automation_tools())
        typed = form_fields_page.fill_message_with_automation_tools()
        with allure.step("Проверить значение поля Message"):
            assert typed == expected
            assert form_fields_page.message_value == "Selenium, Playwright, Cypress, Appium, Katalon Studio"

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("TC-FF-03. Отправка полностью заполненной формы (Message — список инструментов)")
    def test_submit_full_form(self, form_fields_page: FormFieldsPage):
        page = form_fields_page
        page.fill_name("Ivan Petrov")
        page.fill_password("S3cret!pass")
        page.select_drinks("Milk", "Coffee")
        page.select_color("Yellow")
        page.select_automation("Yes")
        page.fill_email("ivan.petrov@example.com")
        page.fill_message_with_automation_tools()
        page.submit()
        with allure.step("Проверить текст alert-сообщения"):
            assert page.wait_alert_text_and_accept() == SUCCESS_ALERT_TEXT
        with allure.step("Проверить, что после отправки форма очищена"):
            assert page.name_value == ""
            assert page.email_value == ""
            assert page.message_value == ""
            assert page.selected_drinks() == []
            assert page.selected_colors() == []

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-FF-04. Отправка формы только с обязательным полем Name")
    def test_submit_with_required_field_only(self, form_fields_page: FormFieldsPage):
        form_fields_page.fill_name("Anna")
        form_fields_page.submit()
        with allure.step("Проверить текст alert-сообщения"):
            assert form_fields_page.wait_alert_text_and_accept() == SUCCESS_ALERT_TEXT

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-FF-05. Можно выбрать несколько напитков и снять отметку")
    def test_multiple_checkboxes(self, form_fields_page: FormFieldsPage):
        form_fields_page.select_drinks("Water", "Wine", "Ctrl-Alt-Delight")
        with allure.step("Проверить, что отмечены три напитка"):
            assert form_fields_page.selected_drinks() == ["Water", "Wine", "Ctrl-Alt-Delight"]
        form_fields_page.unselect_drink("Wine")
        with allure.step("Проверить, что отметка снята только с «Wine»"):
            assert form_fields_page.selected_drinks() == ["Water", "Ctrl-Alt-Delight"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-FF-06. Выбор цвета: радиокнопки взаимоисключающие")
    def test_radio_buttons_are_exclusive(self, form_fields_page: FormFieldsPage):
        form_fields_page.select_color("Red")
        form_fields_page.select_color("#FFC0CB")
        with allure.step("Проверить, что выбран только последний цвет"):
            assert form_fields_page.selected_colors() == ["#FFC0CB"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-FF-07. Выпадающий список «Do you like automation?»")
    def test_automation_dropdown(self, form_fields_page: FormFieldsPage):
        with allure.step("Проверить варианты и значение по умолчанию"):
            assert form_fields_page.automation_options() == ["Yes", "No", "Undecided"]
            assert form_fields_page.automation_value == "default"
        for option, value in (("No", "no"), ("Undecided", "undecided"), ("Yes", "yes")):
            form_fields_page.select_automation(option)
            assert form_fields_page.automation_value == value

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("TC-FF-08. Поле Password скрывает вводимые символы")
    def test_password_is_masked(self, form_fields_page: FormFieldsPage):
        form_fields_page.fill_password("S3cret!pass")
        with allure.step("Проверить тип поля и сохранённое значение"):
            assert form_fields_page.password_input.get_attribute("type") == "password"
            assert form_fields_page.password_input.get_attribute("value") == "S3cret!pass"


@allure.story("Негативные сценарии")
@pytest.mark.negative
class TestFormFieldsNegative:
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-FF-N1. Пустая форма не отправляется: срабатывает валидация поля Name")
    def test_submit_empty_form(self, form_fields_page: FormFieldsPage):
        form_fields_page.submit()
        with allure.step("Проверить, что alert не появился и поле Name невалидно"):
            assert not form_fields_page.alert_appears_within(3)
            value_missing, message = form_fields_page.name_validation()
            assert value_missing
            assert message, "Браузер должен показать подсказку о незаполненном поле"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-FF-N2. Форма без имени не отправляется, введённые данные сохраняются")
    def test_submit_without_name_keeps_data(self, form_fields_page: FormFieldsPage):
        page = form_fields_page
        page.select_drinks("Coffee")
        page.select_color("Blue")
        page.fill_email("ivan.petrov@example.com")
        message = page.fill_message_with_automation_tools()
        page.submit()
        with allure.step("Проверить, что alert не появился, а данные не сброшены"):
            assert not page.alert_appears_within(3)
            assert page.email_value == "ivan.petrov@example.com"
            assert page.message_value == message
            assert page.selected_drinks() == ["Coffee"]
            assert page.selected_colors() == ["Blue"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-FF-N3. Имя, введённое и затем стёртое, снова блокирует отправку")
    def test_cleared_name_blocks_submit(self, form_fields_page: FormFieldsPage):
        form_fields_page.fill_name("Temporary")
        form_fields_page.clear_name()
        form_fields_page.submit()
        with allure.step("Проверить, что alert не появился и поле Name невалидно"):
            assert not form_fields_page.alert_appears_within(3)
            assert form_fields_page.name_validation()[0]
