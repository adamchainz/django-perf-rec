in_pytest = False


def pytest_configure() -> None:
    global in_pytest
    in_pytest = True
