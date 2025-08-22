from __future__ import annotations
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

def find(driver: WebDriver, by_value):
    """Find a single element. Accepts either a locator tuple or a CSS selector string."""
    if isinstance(by_value, tuple):
        return driver.find_element(*by_value)
    return driver.find_element(By.CSS_SELECTOR, by_value)

def finds(driver: WebDriver, by_value):
    if isinstance(by_value, tuple):
        return driver.find_elements(*by_value)
    return driver.find_elements(By.CSS_SELECTOR, by_value)

class Shadow:
    """Helper for piercing Shadow DOM trees using JS."""
    @staticmethod
    def root(driver: WebDriver, host):
        return driver.execute_script("return arguments[0].shadowRoot", host)

    @staticmethod
    def query(driver: WebDriver, host, selector: str):
        return driver.execute_script("return arguments[0].shadowRoot.querySelector(arguments[1])", host, selector)

    @staticmethod
    def query_all(driver: WebDriver, host, selector: str):
        return driver.execute_script("return arguments[0].shadowRoot.querySelectorAll(arguments[1])", host, selector)