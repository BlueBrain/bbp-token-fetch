from keycloak import KeycloakAuthenticationError

from blue_brain_token_fetch.token_fetcher_service import TokenFetcherService
from tests.conftest import SERVICE_CONFIG

import pytest


def test_service_account(service_username, service_password):
    test = TokenFetcherService(
        keycloak_config_file=SERVICE_CONFIG, username=service_username, password=service_password
    )

    token = test.get_access_token()
    duration = test.get_access_token_duration()
    assert token is not None
    assert duration is not None


def test_invalid_credentials(service_username):
    with pytest.raises(KeycloakAuthenticationError):
        TokenFetcherService(
            service_username,
            "password",
            SERVICE_CONFIG,
        )
