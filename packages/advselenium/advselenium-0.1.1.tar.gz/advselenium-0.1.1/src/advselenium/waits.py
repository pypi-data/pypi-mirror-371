from __future__ import annotations
from typing import Callable, Tuple, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

class SmartWait:
    """Convenience wrapper around WebDriverWait with retries and sugar."""
    def __init__(self, driver, timeout: int = 20, poll: float = 0.25):
        self.driver = driver
        self.timeout = timeout
        self.poll = poll

    def until(self, condition: Callable, timeout: Optional[int] = None):
        t = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, t, poll_frequency=self.poll).until(condition)
        except TimeoutException as e:
            from .exceptions import WaitTimeout
            raise WaitTimeout(str(e))

    def visible(self, locator: Tuple[str, str]):
        return self.until(EC.visibility_of_element_located(locator))

    def clickable(self, locator: Tuple[str, str]):
        return self.until(EC.element_to_be_clickable(locator))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2),
           retry=retry_if_exception_type(StaleElementReferenceException))
    def safe_click(self, element):
        element.click()
        return True

# re-export common things
EC = EC
By = By