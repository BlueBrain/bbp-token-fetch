import pytest


SERVICE_CONFIG = "./tests/tests_data/service_keycloak_config.yaml"
REGULAR_CONFIG = "./tests/tests_data/regular_keycloak_config.yaml"


def pytest_addoption(parser):
    parser.addoption("--regular_username", action="store", required=True)
    parser.addoption("--regular_password", action="store", required=True)
    parser.addoption("--service_username", action="store", required=True)
    parser.addoption("--service_password", action="store", required=True)


@pytest.fixture(scope="session")
def regular_username(pytestconfig):
    return pytestconfig.getoption("regular_username")


@pytest.fixture(scope="session")
def regular_password(pytestconfig):
    return pytestconfig.getoption("regular_password")

@pytest.fixture(scope="session")
def service_username(pytestconfig):
    return pytestconfig.getoption("service_username")

@pytest.fixture(scope="session")
def service_password(pytestconfig):
    return pytestconfig.getoption("service_password")