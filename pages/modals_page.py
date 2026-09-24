"""Страница «Modals»: https://practice-automation.com/modals/"""

from __future__ import annotations

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage
from pages.components.jetpack_form import JetpackForm
from pages.components.popup import Popup

# Идентификаторы окон в плагине Popup Maker (id записи WordPress, стабильны).
SIMPLE_MODAL_ID = 1318
FORM_MODAL_ID = 674


class ContactFormModal(Popup):
    """Модальное окно «Modal Containing A Form» с формой обратной связи."""

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver, FORM_MODAL_ID, "Modal Containing A Form")
        root = f"{self.css_root} [data-test='contact-form']"
        self.form = JetpackForm(driver, root)
        self.INTRO = (By.CSS_SELECTOR, f"{self.css_root} .pum-content > p strong")
        self.NAME_INPUT = (By.CSS_SELECTOR, f"{root} input[name$='-name']")
        self.NAME_LABEL = (By.CSS_SELECTOR, f"{root} label.grunion-field-label.name")
        self.EMAIL_INPUT = (By.CSS_SELECTOR, f"{root} input[type='email']")
        # В форме есть ещё скрытая textarea-ловушка для спама (Akismet), поэтому уточняем класс
        self.MESSAGE_INPUT = (By.CSS_SELECTOR, f"{root} textarea.grunion-field")

    @property
    def intro_text(self) -> str:
        return self.text_of(self.INTRO)

    @property
    def name_input(self) -> WebElement:
        return self.find_visible(self.NAME_INPUT)

    @property
    def email_input(self) -> WebElement:
        return self.find_visible(self.EMAIL_INPUT)

    @property
    def message_input(self) -> WebElement:
        return self.find_visible(self.MESSAGE_INPUT)

    @property
    def name_label(self) -> str:
        return self.text_of(self.NAME_LABEL)

    def fill(self, name: str = "", email: str = "", message: str = "") -> None:
        with allure.step(f"Заполнить форму: Name=«{name}», Email=«{email}», Message=«{message}»"):
            if name:
                self.type_text(self.NAME_INPUT, name)
            if email:
                self.type_text(self.EMAIL_INPUT, email)
            if message:
                self.type_text(self.MESSAGE_INPUT, message)


class ModalsPage(BasePage):
    PATH = "/modals/"

    SIMPLE_MODAL_BUTTON = (By.ID, "simpleModal")
    FORM_MODAL_BUTTON = (By.ID, "formModal")

    def __init__(self, driver: WebDriver, base_url: str | None = None) -> None:
        super().__init__(driver, base_url)
        self.simple_modal = Popup(driver, SIMPLE_MODAL_ID, "Simple Modal")
        self.form_modal = ContactFormModal(driver)

    def is_simple_modal_button_displayed(self) -> bool:
        return self.is_visible(self.SIMPLE_MODAL_BUTTON)

    def is_form_modal_button_displayed(self) -> bool:
        return self.is_visible(self.FORM_MODAL_BUTTON)

    def open_simple_modal(self) -> Popup:
        with allure.step("Нажать кнопку «Simple Modal»"):
            self.click(self.SIMPLE_MODAL_BUTTON)
        self.simple_modal.wait_opened()
        return self.simple_modal

    def open_form_modal(self) -> ContactFormModal:
        with allure.step("Нажать кнопку «Form Modal»"):
            self.click(self.FORM_MODAL_BUTTON)
        self.form_modal.wait_opened()
        return self.form_modal
