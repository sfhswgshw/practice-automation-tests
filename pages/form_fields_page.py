"""Страница с формой «Form Fields»: https://practice-automation.com/form-fields/

На этой странице выполняется п.5 задания: список из раздела
«Automation tools» считывается средствами Selenium, преобразуется в текст
и через запятую вводится в поле «Message».
"""

from __future__ import annotations

import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage

SUCCESS_ALERT_TEXT = "Message received!"


class FormFieldsPage(BasePage):
    PATH = "/form-fields/"

    FORM = (By.ID, "feedbackForm")
    NAME_INPUT = (By.ID, "name-input")
    PASSWORD_INPUT = (By.XPATH, "//form[@id='feedbackForm']//label[contains(., 'Password')]/input")
    DRINKS = (By.CSS_SELECTOR, "input[name='fav_drink']")
    COLORS = (By.CSS_SELECTOR, "input[name='fav_color']")
    AUTOMATION_SELECT = (By.ID, "automation")
    # Пункты списка, который идёт сразу после подписи «Automation tools»
    AUTOMATION_TOOLS = (
        By.XPATH,
        "//form[@id='feedbackForm']//label[normalize-space()='Automation tools']"
        "/following-sibling::ul[1]/li",
    )
    EMAIL_INPUT = (By.ID, "email")
    MESSAGE_INPUT = (By.ID, "message")
    SUBMIT_BUTTON = (By.ID, "submit-btn")

    def __init__(self, driver: WebDriver, base_url: str | None = None) -> None:
        super().__init__(driver, base_url)

    # ---------- Automation tools / Message (п.5 задания) ----------
    def automation_tools(self) -> list[str]:
        with allure.step("Получить список элементов из раздела «Automation tools»"):
            self.find_visible(self.AUTOMATION_TOOLS)
            tools = [li.text.strip() for li in self.find_all(self.AUTOMATION_TOOLS)]
            allure.attach("\n".join(tools), name="Automation tools")
            return tools

    def fill_message_with_automation_tools(self) -> str:
        """Заполняет Message списком инструментов через запятую и возвращает этот текст."""
        text = ", ".join(self.automation_tools())
        self.fill_message(text)
        return text

    # ---------- заполнение полей ----------
    @allure.step("Ввести имя «{name}»")
    def fill_name(self, name: str) -> None:
        self.type_text(self.NAME_INPUT, name)

    @allure.step("Ввести пароль")
    def fill_password(self, password: str) -> None:
        self.type_text(self.PASSWORD_INPUT, password)

    def select_drinks(self, *drinks: str) -> None:
        with allure.step(f"Отметить любимые напитки: {', '.join(drinks)}"):
            for drink in drinks:
                self._check(self._drink(drink))

    @allure.step("Снять отметку с напитка «{drink}»")
    def unselect_drink(self, drink: str) -> None:
        checkbox = self._drink(drink)
        if checkbox.is_selected():
            self.scroll_into_view(checkbox).click()

    @allure.step("Выбрать любимый цвет «{color}»")
    def select_color(self, color: str) -> None:
        self._check(self._color(color))

    @allure.step("Выбрать в списке «Do you like automation?» значение «{option}»")
    def select_automation(self, option: str) -> None:
        select_element = self.find_visible(self.AUTOMATION_SELECT)
        self.scroll_into_view(select_element)
        Select(select_element).select_by_visible_text(option)

    @allure.step("Ввести email «{email}»")
    def fill_email(self, email: str) -> None:
        self.type_text(self.EMAIL_INPUT, email)

    @allure.step("Ввести сообщение «{message}»")
    def fill_message(self, message: str) -> None:
        self.type_text(self.MESSAGE_INPUT, message)

    @allure.step("Очистить поле «Name»")
    def clear_name(self) -> None:
        field = self.name_input
        field.clear()

    @allure.step("Нажать кнопку «Submit»")
    def submit(self) -> None:
        self.click(self.SUBMIT_BUTTON)

    # ---------- alert ----------
    def wait_alert_text_and_accept(self) -> str:
        with allure.step("Дождаться alert-сообщения и нажать «OK»"):
            alert = self.wait().until(EC.alert_is_present(), message="Alert не появился")
            text = alert.text
            alert.accept()
            allure.attach(text, name="Текст alert")
            return text

    def alert_appears_within(self, seconds: float = 3) -> bool:
        with allure.step(f"Проверить, появляется ли alert в течение {seconds} с"):
            try:
                alert = self.wait(seconds).until(EC.alert_is_present())
            except TimeoutException:
                return False
            alert.accept()
            return True

    # ---------- состояние ----------
    @property
    def name_input(self) -> WebElement:
        return self.find_visible(self.NAME_INPUT)

    @property
    def password_input(self) -> WebElement:
        return self.find_visible(self.PASSWORD_INPUT)

    @property
    def name_value(self) -> str:
        return self.value_of(self.NAME_INPUT)

    @property
    def email_value(self) -> str:
        return self.value_of(self.EMAIL_INPUT)

    @property
    def message_value(self) -> str:
        return self.value_of(self.MESSAGE_INPUT)

    def selected_drinks(self) -> list[str]:
        return [cb.get_attribute("value") for cb in self.find_all(self.DRINKS) if cb.is_selected()]

    def selected_colors(self) -> list[str]:
        return [rb.get_attribute("value") for rb in self.find_all(self.COLORS) if rb.is_selected()]

    def automation_options(self) -> list[str]:
        select = Select(self.find(self.AUTOMATION_SELECT))
        return [o.text.strip() for o in select.options if o.text.strip()]

    @property
    def automation_value(self) -> str:
        return self.value_of(self.AUTOMATION_SELECT)

    def name_validation(self) -> tuple[bool, str]:
        """(valueMissing, validationMessage) встроенной HTML5-валидации поля Name."""
        field = self.find(self.NAME_INPUT)
        missing = self.driver.execute_script("return arguments[0].validity.valueMissing;", field)
        return bool(missing), field.get_attribute("validationMessage") or ""

    # ---------- внутреннее ----------
    def _drink(self, value: str) -> WebElement:
        return self.find((By.CSS_SELECTOR, f"input[name='fav_drink'][value='{value}']"))

    def _color(self, value: str) -> WebElement:
        return self.find((By.CSS_SELECTOR, f"input[name='fav_color'][value='{value}']"))

    def _check(self, element: WebElement) -> None:
        if not element.is_selected():
            self.scroll_into_view(element)
            element.click()
