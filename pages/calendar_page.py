"""Страница «Calendars»: https://practice-automation.com/calendars/"""

from __future__ import annotations

import datetime as dt

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage
from pages.components.date_picker import DatePicker
from pages.components.jetpack_form import JetpackForm

FORM_ROOT = ".entry-content [data-test='contact-form']"


class CalendarPage(BasePage):
    PATH = "/calendars/"

    DATE_INPUT = (By.CSS_SELECTOR, f"{FORM_ROOT} input.jp-contact-form-date")
    DATE_LABEL = (By.CSS_SELECTOR, f"{FORM_ROOT} label.grunion-field-label")
    DATE_FORMAT_HINT = (By.CSS_SELECTOR, f"{FORM_ROOT} .contact-form__field-format")

    def __init__(self, driver: WebDriver, base_url: str | None = None) -> None:
        super().__init__(driver, base_url)
        self.date_picker = DatePicker(driver)
        self.form = JetpackForm(driver, FORM_ROOT)

    # ---------- элементы ----------
    @property
    def date_input(self) -> WebElement:
        return self.find_visible(self.DATE_INPUT)

    @property
    def date_value(self) -> str:
        return self.value_of(self.DATE_INPUT)

    @property
    def date_label(self) -> str:
        return self.text_of(self.DATE_LABEL)

    @property
    def date_format_hint(self) -> str:
        return self.text_of(self.DATE_FORMAT_HINT)

    # ---------- действия ----------
    @allure.step("Кликнуть в поле даты и дождаться открытия календаря")
    def open_date_picker(self) -> DatePicker:
        self.click(self.DATE_INPUT)
        self.date_picker.wait_opened()
        return self.date_picker

    @allure.step("Ввести в поле даты с клавиатуры: «{text}»")
    def enter_date(self, text: str) -> None:
        self.type_text(self.DATE_INPUT, text)

    @allure.step("Закрыть календарь клавишей Esc")
    def close_date_picker_with_escape(self) -> None:
        self.date_input.send_keys(Keys.ESCAPE)
        self.date_picker.wait_closed()

    def select_date(self, date: dt.date) -> None:
        self.open_date_picker().select_date(date)

    def select_date_via_dropdowns(self, date: dt.date) -> None:
        self.open_date_picker().select_date_via_dropdowns(date)

    @allure.step("Выбрать следующий за сегодняшним день с клавиатуры (↓, →, Enter)")
    def select_tomorrow_with_keyboard(self) -> None:
        self.open_date_picker()
        # ↓ переводит фокус из поля в календарь на подсвеченный (сегодняшний) день
        self.date_input.send_keys(Keys.ARROW_DOWN)
        self.wait().until(
            lambda d: "dp-day" in (d.switch_to.active_element.get_attribute("class") or ""),
            message="Фокус не перешёл в календарь",
        )
        self.driver.switch_to.active_element.send_keys(Keys.ARROW_RIGHT)
        self.driver.switch_to.active_element.send_keys(Keys.ENTER)
        self.date_picker.wait_closed()

    def submit_date(self, text: str) -> None:
        """Ввести дату вручную, закрыть календарь и отправить форму."""
        self.enter_date(text)
        self.close_date_picker_with_escape()
        self.form.submit()
