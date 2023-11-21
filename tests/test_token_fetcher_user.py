from keycloak import KeycloakAuthenticationError, KeycloakPostError, KeycloakConnectionError

from blue_brain_token_fetch.token_fetcher_user import TokenFetcherUser
from tests.conftest import REGULAR_CONFIG

import pytest


def test_regular_account(regular_username, regular_password):
    test = TokenFetcherUser(
        keycloak_config_file=REGULAR_CONFIG, username=regular_username, password=regular_password
    )

    token = test.get_access_token()
    duration = test.get_access_token_duration()
    assert token is not None
    assert duration is not None


def test_invalid_credentials(regular_username):
    with pytest.raises(KeycloakAuthenticationError):
        TokenFetcherUser(
            regular_username,
            "password",
            REGULAR_CONFIG,
        )


def test_invalid_config_file():
    with pytest.raises(ValueError):
        TokenFetcherUser(
            "username",
            "password",
            "./tests/tests_data/empty_keycloak_config.yaml",
        )
    with pytest.raises(KeyError):  # missing client id
        TokenFetcherUser(
            "username",
            "password",
            "./tests/tests_data/service_keycloak_config.yaml",
        )
    with pytest.raises(KeycloakPostError):  # Invalid realm
        TokenFetcherUser(
            "username",
            "password",
            "./tests/tests_data/regular_keycloak_config_invalid_realm.yaml",
        )
    with pytest.raises(KeycloakConnectionError):  # Invalid server url
        TokenFetcherUser(
            "username",
            "password",
            "./tests/tests_data/regular_keycloak_config_invalid_server_url.yaml",
        )
    with pytest.raises(KeycloakAuthenticationError):  # Invalid client id
        TokenFetcherUser(
            "username",
            "password",
            "./tests/tests_data/regular_keycloak_config_invalid_client_id.yaml",
        )


def test_non_existing_config_file():
    with pytest.raises(FileNotFoundError):
        TokenFetcherUser(
            "username",
            "password",
            "non existent config file",
        )
