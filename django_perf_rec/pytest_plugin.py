in_pytest = False


def pytest_configure(config):
    global in_pytest
    in_pytest = True
