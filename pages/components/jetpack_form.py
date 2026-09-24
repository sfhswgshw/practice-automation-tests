"""Компонент формы Jetpack Forms (WordPress).

На сайте этой формой сделаны и поле даты на странице «Calendars»,
и форма обратной связи внутри модального окна. Разметка у них общая:

* контейнер ``[data-test='contact-form']``;
* у каждого поля ввода ``aria-describedby`` указывает на элемент
  с текстом ошибки валидации этого поля;
* общий блок ошибок формы — ``.contact-form__error.show-errors``;
* после успешной AJAX-отправки показывается блок
  ``.contact-form-submission.submission-success`` со сводкой отправленных полей.
"""

from __future__ import annotations

import unicodedata

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BaseElement, Locator

SUCCESS_TITLE = "Thank you for your response."


class JetpackForm(BaseElement):
    SUBMIT_TIMEOUT = 20  # отправка идёт на сервер, даём запас

    def __init__(self, driver: WebDriver, root_css: str) -> None:
        super().__init__(driver)
        self.root_css = root_css
        self.SUBMIT_BUTTON: Locator = (By.CSS_SELECTOR, f"{root_css} form button[type='submit']")
        self.SUCCESS_BLOCK: Locator = (
            By.CSS_SELECTOR,
            f"{root_css} .contact-form-submission.submission-success",
        )
        self.SUCCESS_TITLE: Locator = (By.CSS_SELECTOR, f"{root_css} .submission-success h4")
        self.SUMMARY_ITEMS: Locator = (
            By.CSS_SELECTOR,
            f"{root_css} .submission-success .jetpack_forms_contact-form-success-summary",
        )
        self.BACK_LINK: Locator = (By.CSS_SELECTOR, f"{root_css} .submission-success .go-back-message a")
        self.FORM_ERROR: Locator = (
            By.CSS_SELECTOR,
            f"{root_css} .contact-form__error.show-errors .contact-form__error-message",
        )
        self.FORM_ERROR_ITEMS: Locator = (
            By.CSS_SELECTOR,
            f"{root_css} .contact-form__error.show-errors ul li",
        )

    # ---------- действия ----------
    @allure.step("Нажать кнопку «Submit»")
    def submit(self) -> None:
        self.click(self.SUBMIT_BUTTON)

    @allure.step("Нажать ссылку «← Back» в сообщении об успешной отправке")
    def go_back(self) -> None:
        self.click(self.BACK_LINK)
        self.wait_invisible(self.SUCCESS_BLOCK)

    # ---------- состояние ----------
    def wait_success(self) -> None:
        with allure.step("Дождаться сообщения об успешной отправке формы"):
            self.find_visible(self.SUCCESS_BLOCK, self.SUBMIT_TIMEOUT)

    def is_success_displayed(self) -> bool:
        return self.is_visible(self.SUCCESS_BLOCK)

    def success_not_displayed_within(self, seconds: float = 5) -> bool:
        with allure.step(f"Убедиться, что сообщение об успехе не появилось за {seconds} с"):
            return self.stays_invisible(self.SUCCESS_BLOCK, seconds)

    @property
    def success_title(self) -> str:
        """Заголовок сообщения об успехе без эмодзи.

        В заголовке есть «✨»: Chrome получает его от WordPress картинкой <img>,
        а Firefox — обычным символом в тексте. Убираем символы-эмодзи (категория So),
        чтобы проверка одинаково работала в обоих браузерах.
        """
        text = self.text_of(self.SUCCESS_TITLE)
        return "".join(ch for ch in text if unicodedata.category(ch) != "So" and ch != "\ufe0f").strip()

    def submitted_values(self) -> dict[str, str]:
        """Сводка отправленных данных: {'Name': 'Ivan', 'Email': ...}."""
        result: dict[str, str] = {}
        for item in self.find_all(self.SUMMARY_ITEMS):
            name = item.find_element(By.CSS_SELECTOR, ".field-name").text.strip().rstrip(":")
            value = item.find_element(By.CSS_SELECTOR, ".field-value").text.strip()
            result[name] = value
        return result

    def is_submit_button_displayed(self) -> bool:
        return self.is_visible(self.SUBMIT_BUTTON)

    # ---------- ошибки валидации ----------
    def field_error(self, field: WebElement) -> str:
        """Текст ошибки, привязанной к полю через aria-describedby."""
        described_by = (field.get_attribute("aria-describedby") or "").split()
        error_ids = [i for i in described_by if "error" in i]
        if not error_ids:
            return ""
        return self.driver.find_element(By.ID, error_ids[0]).text.strip()

    def wait_field_error(self, field: WebElement) -> str:
        with allure.step("Дождаться сообщения об ошибке под полем"):
            self.wait().until(
                lambda _: self.field_error(field),
                message="Сообщение об ошибке под полем не появилось",
            )
            return self.field_error(field)

    @staticmethod
    def is_marked_invalid(field: WebElement) -> bool:
        return field.get_attribute("aria-invalid") == "true"

    @property
    def form_error(self) -> str:
        return self.text_of(self.FORM_ERROR)

    def form_error_items(self) -> list[str]:
        return [li.text.strip() for li in self.find_all(self.FORM_ERROR_ITEMS) if li.text.strip()]
