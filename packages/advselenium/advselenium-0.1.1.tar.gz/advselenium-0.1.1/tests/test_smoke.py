def test_import():
    import advselenium
    assert hasattr(advselenium, "create_driver")