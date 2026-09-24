"""Тесты страницы «Modals» — https://practice-automation.com/modals/"""

from __future__ import annotations

import allure
import pytest

from pages.components.jetpack_form import SUCCESS_TITLE
from pages.modals_page import ModalsPage

REQUIRED_ERROR = "This field is required."
EMAIL_ERROR = "Please enter a valid email address"
FORM_ERROR = "Please fill out the form correctly."

pytestmark = [allure.epic("UI practice-automation.com"), allure.feature("Модальные окна")]


def _normalize(text: str) -> str:
    """Типографский апостроф ’ на сайте приводим к обычному '."""
    return text.replace("’", "'")


@allure.story("Позитивные сценарии")
@pytest.mark.positive
class TestModalsPositive:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-MOD-01. На странице есть кнопки открытия окон, окна изначально скрыты")
    def test_page_initial_state(self, modals_page: ModalsPage):
        with allure.step("Проверить заголовок страницы и кнопки"):
            assert modals_page.heading == "Modals"
            assert modals_page.is_simple_modal_button_displayed()
            assert modals_page.is_form_modal_button_displayed()
        with allure.step("Проверить, что ни одно окно не открыто"):
            assert not modals_page.simple_modal.is_opened()
            assert not modals_page.form_modal.is_opened()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-MOD-02. Открытие простого модального окна и его содержимое")
    def test_open_simple_modal(self, modals_page: ModalsPage):
        modal = modals_page.open_simple_modal()
        with allure.step("Проверить заголовок, текст и кнопку закрытия"):
            assert modal.title == "Simple Modal"
            assert _normalize(modal.content_text) == "Hi, I'm a simple modal."
            assert modal.is_close_button_displayed()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-MOD-03. Закрытие простого модального окна кнопкой «×»")
    def test_close_simple_modal(self, modals_page: ModalsPage):
        modal = modals_page.open_simple_modal()
        modal.close()
        modal.wait_closed()
        with allure.step("Проверить, что окно закрыто"):
            assert not modal.is_opened()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-MOD-04. Простое модальное окно можно открыть повторно после закрытия")
    def test_reopen_simple_modal(self, modals_page: ModalsPage):
        for attempt in (1, 2):
            with allure.step(f"Открытие и закрытие окна, попытка {attempt}"):
                modal = modals_page.open_simple_modal()
                assert modal.title == "Simple Modal"
                modal.close()
                modal.wait_closed()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-MOD-05. Открытие окна с формой: заголовок и поля формы")
    def test_open_form_modal(self, modals_page: ModalsPage):
        modal = modals_page.open_form_modal()
        with allure.step("Проверить заголовок, пояснение и поля формы"):
            assert modal.title == "Modal Containing A Form"
            assert modal.intro_text == "Please enter your contact info below."
            assert modal.name_input.is_displayed()
            assert "required" in modal.name_label.lower(), "Поле Name должно быть обязательным"
            assert modal.email_input.is_displayed()
            assert modal.message_input.is_displayed()
            assert modal.form.is_submit_button_displayed()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-MOD-06. Закрытие окна с формой клавишей Esc")
    def test_close_form_modal_with_escape(self, modals_page: ModalsPage):
        modal = modals_page.open_form_modal()
        modal.press_escape()
        modal.wait_closed()
        with allure.step("Проверить, что окно закрыто"):
            assert not modal.is_opened()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-MOD-07. Закрытие окна с формой кнопкой «×»")
    def test_close_form_modal_with_button(self, modals_page: ModalsPage):
        modal = modals_page.open_form_modal()
        modal.close()
        modal.wait_closed()
        with allure.step("Проверить, что окно закрыто"):
            assert not modal.is_opened()

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("TC-MOD-08. Отправка формы в модальном окне со всеми заполненными полями")
    def test_submit_form_with_all_fields(self, modals_page: ModalsPage):
        data = {"Name": "Ivan Petrov", "Email": "ivan.petrov@example.com", "Message": "Hello from autotest"}
        modal = modals_page.open_form_modal()
        modal.fill(name=data["Name"], email=data["Email"], message=data["Message"])
        modal.form.submit()
        modal.form.wait_success()
        with allure.step("Проверить сообщение об успехе и сводку отправленных данных"):
            assert modal.form.success_title == SUCCESS_TITLE
            assert modal.form.submitted_values() == data
            assert modal.is_opened(), "После отправки окно остаётся открытым с результатом"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-MOD-09. Отправка формы только с обязательным полем Name")
    def test_submit_form_with_required_field_only(self, modals_page: ModalsPage):
        modal = modals_page.open_form_modal()
        modal.fill(name="Anna")
        modal.form.submit()
        modal.form.wait_success()
        with allure.step("Проверить сообщение об успехе и отправленное имя"):
            assert modal.form.success_title == SUCCESS_TITLE
            assert modal.form.submitted_values().get("Name") == "Anna"


@allure.story("Негативные сценарии")
@pytest.mark.negative
class TestModalsNegative:
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("TC-MOD-N1. Простое модальное окно не закрывается клавишей Esc")
    def test_simple_modal_is_not_closed_by_escape(self, modals_page: ModalsPage):
        modal = modals_page.open_simple_modal()
        modal.press_escape()
        with allure.step("Проверить, что окно осталось открытым"):
            assert modal.stays_opened(2)

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("TC-MOD-N2. Простое модальное окно не закрывается кликом по затемнённой области")
    def test_simple_modal_is_not_closed_by_overlay_click(self, modals_page: ModalsPage):
        modal = modals_page.open_simple_modal()
        modal.click_on_overlay()
        with allure.step("Проверить, что окно осталось открытым"):
            assert modal.stays_opened(2)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-MOD-N3. Отправка пустой формы: ошибка обязательного поля Name")
    def test_submit_empty_form(self, modals_page: ModalsPage):
        modal = modals_page.open_form_modal()
        modal.form.submit()
        error = modal.form.wait_field_error(modal.name_input)
        with allure.step("Проверить ошибки валидации и то, что форма не отправлена"):
            assert error == REQUIRED_ERROR
            assert modal.form.is_marked_invalid(modal.name_input)
            assert modal.form.form_error == FORM_ERROR
            assert not modal.form.is_success_displayed()
            assert modal.is_opened()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-MOD-N4. Некорректный email «{email}» не принимается")
    @pytest.mark.parametrize("email", ["ivan.petrov@", "ivan.petrov.example.com"], ids=["no-domain", "no-at"])
    def test_invalid_email(self, modals_page: ModalsPage, email: str):
        modal = modals_page.open_form_modal()
        modal.fill(name="Ivan Petrov", email=email, message="Test")
        modal.form.submit()
        error = modal.form.wait_field_error(modal.email_input)
        with allure.step("Проверить ошибку поля Email и то, что форма не отправлена"):
            assert error == EMAIL_ERROR
            assert modal.form.is_marked_invalid(modal.email_input)
            assert modal.form.field_error(modal.name_input) == "", "У корректного Name ошибки быть не должно"
            assert not modal.form.is_success_displayed()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-MOD-N5. Форма с email и сообщением, но без имени, не отправляется")
    def test_submit_without_name(self, modals_page: ModalsPage):
        modal = modals_page.open_form_modal()
        modal.fill(email="ivan.petrov@example.com", message="No name here")
        modal.form.submit()
        error = modal.form.wait_field_error(modal.name_input)
        with allure.step("Проверить, что ошибка только у поля Name, а введённые данные сохранились"):
            assert error == REQUIRED_ERROR
            assert modal.form.field_error(modal.email_input) == ""
            assert modal.email_input.get_attribute("value") == "ivan.petrov@example.com"
            assert not modal.form.is_success_displayed()
