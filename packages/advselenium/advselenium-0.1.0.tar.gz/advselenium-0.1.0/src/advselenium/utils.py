from __future__ import annotations
from pathlib import Path
import time

def screenshot_artifact(driver, path: str | Path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(p))
    return p

def save_html_artifact(driver, path: str | Path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(driver.page_source, encoding="utf-8")
    return p

def human_delay(min_s: float = 0.2, max_s: float = 0.6):
    import random, time
    time.sleep(random.uniform(min_s, max_s))