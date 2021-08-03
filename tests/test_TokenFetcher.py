import os
import pytest
from blue_brain_token_fetch.Token_refresher import TokenFetcher


def test_TokenFetcher():

    # KeycloakAuthenticationError
    username = "username"
    password = "password"
    keycloak_config_file = f"{os.environ.get('HOME', '')}/keycloack_config.yaml"

    # a = vars(TokenFetcher(
    #         username,
    #         password,
    #         keycloak_config_file,
    #     ))
    # assert a == "'NoneType' object is not subscriptable"

    # TypeError
    keycloak_config_file = f"{os.environ.get('HOME', '')}/keycloack_config.yaml"

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
