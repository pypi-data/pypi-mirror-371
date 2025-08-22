from __future__ import annotations
from typing import Tuple
from selenium.webdriver.common.by import By
from .waits import SmartWait
from .elements import find

Locator = Tuple[str, str]

class BasePage:
    url: str | None = None
    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = SmartWait(driver, timeout=timeout)

    def open(self):
        if not self.url:
            raise ValueError("No URL specified for this page.")
        self.driver.get(self.url)
        return self

    def visible(self, locator: Locator):
        return self.wait.visible(locator)

class BaseComponent:
    def __init__(self, root):
        self.root = root

    def el(self, locator: Locator):
        return find(self.root, locator)