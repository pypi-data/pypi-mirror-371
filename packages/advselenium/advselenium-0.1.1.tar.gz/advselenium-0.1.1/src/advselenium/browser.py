from __future__ import annotations
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

class ChromeOptionsBuilder:
    def __init__(self):
        self.options = ChromeOptions()
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        # sensible defaults for stability
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)

    def headless(self, value: bool = True) -> "ChromeOptionsBuilder":
        if value:
            self.options.add_argument("--headless=new")
        return self

    def user_agent(self, ua: str) -> "ChromeOptionsBuilder":
        self.options.add_argument(f"--user-agent={ua}")
        return self

    def add_args(self, *args: str) -> "ChromeOptionsBuilder":
        for a in args:
            self.options.add_argument(a)
        return self

    def set_prefs(self, prefs: Dict[str, Any]) -> "ChromeOptionsBuilder":
        self.options.add_experimental_option("prefs", prefs)
        return self

    def build(self) -> ChromeOptions:
        return self.options

class FirefoxOptionsBuilder:
    def __init__(self):
        self.options = FirefoxOptions()
        self.options.set_preference("dom.webdriver.enabled", False)
        self.options.set_preference("useAutomationExtension", False)

    def headless(self, value: bool = True) -> "FirefoxOptionsBuilder":
        self.options.headless = value
        return self

    def add_args(self, *args: str) -> "FirefoxOptionsBuilder":
        for a in args:
            self.options.add_argument(a)
        return self

    def build(self) -> FirefoxOptions:
        return self.options

def create_driver(browser: str = "chrome",
                  headless: bool = False,
                  prefs: Optional[Dict[str, Any]] = None,
                  **kwargs) -> webdriver.Remote:
    """Create a Selenium driver with webdriver-manager and sensible defaults."""
    browser = browser.lower()
    if browser == "chrome":
        builder = ChromeOptionsBuilder().headless(headless)
        if prefs:
            builder.set_prefs(prefs)
        options = builder.build()
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options, **kwargs)
    elif browser in ("firefox", "ff"):
        options = FirefoxOptionsBuilder().headless(headless).build()
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options, **kwargs)
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(0)
    return driver