class AdvSeleniumError(Exception):
    """Base exception for advselenium."""

class WaitTimeout(AdvSeleniumError):
    pass

class ElementActionError(AdvSeleniumError):
    pass