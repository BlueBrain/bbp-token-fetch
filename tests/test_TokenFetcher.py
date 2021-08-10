import pytest
from blue_brain_token_fetch.Token_refresher import TokenFetcher


def test_TokenFetcher():

    # KeycloakAuthenticationError
    username = "username"
    password = "password"
    keycloak_config_file = "./tests/tests_data/empty_keycloack_config.yaml"

    # TypeError
    with pytest.raises(SystemExit) as e:
        TokenFetcher(
            username,
            password,
            keycloak_config_file,
        )
    assert e.value.code == 1

    # OSerror
    keycloak_config_file = "non existent config file"

    with pytest.raises(SystemExit) as e:
        TokenFetcher(
            username,
            password,
            keycloak_config_file,
        )
    assert e.value.code == 1

    # KeycloakError
    with pytest.raises(SystemExit) as e:
        TokenFetcher(
            username,
            password,
        )
    assert e.value.code == 1
