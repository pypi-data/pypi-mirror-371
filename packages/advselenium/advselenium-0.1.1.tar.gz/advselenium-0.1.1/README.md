# advselenium

Advanced Selenium toolkit: smart waits, resilient actions, stealth/undetected options, POM base, robust logging & screenshots, and a tiny CLI.

## Quickstart

```bash
pip install .
advsel --help
```

## Highlights
- **SmartWait**: rich waiting utilities, conditions, and timeouts.
- **Resilient actions** with retries (powered by `tenacity`).
- **Stealth**: automatic headless, user-agent rotation, and webdriver-manager integration.
- **POM base classes** (`BasePage`, `BaseComponent`) with ergonomics.
- **Shadow DOM** helpers.
- **Network-aware** download waits (via `performance_log` polling where available).
- **Artifacts**: screenshots-on-failure, HTML source dumps, and structured logs.
- **CLI**: smoke-test a URL quickly or run a simple script.

## Minimal Example

```python
from advselenium import create_driver, SmartWait, By
drv = create_driver(browser="chrome", headless=True)
try:
    drv.get("https://example.org")
    SmartWait(drv).visible((By.CSS_SELECTOR, "h1"))
    print(drv.title)
finally:
    drv.quit()
```
