import os
from typing import Type
from contextlib import nullcontext as does_not_raise

import pytest

from blue_brain_token_fetch.token_fetcher_user import TokenFetcherUser
from blue_brain_token_fetch.token_fetcher_base import TokenFetcherBase
from blue_brain_token_fetch.token_fetcher_service import TokenFetcherService
from tests.conftest import SERVICE_CONFIG, REGULAR_CONFIG, REGULAR_CONFIG_WITH_CLIENT_PWD


@pytest.mark.parametrize("class_to_use, keycloak_config_filepath, expected_size, exception", [
    pytest.param(
        TokenFetcherService, SERVICE_CONFIG, 2, does_not_raise(), id="sa"
    ),
    pytest.param(
        TokenFetcherUser, REGULAR_CONFIG, 3, does_not_raise(), id="non_sa"
    ),
    pytest.param(
        TokenFetcherUser, REGULAR_CONFIG_WITH_CLIENT_PWD, 4, does_not_raise(), id="non_sa_pwd"
    )
])
def test_config_file(
        class_to_use: Type[TokenFetcherBase], keycloak_config_filepath, expected_size, exception
):
    with exception:
        keycloak_config = class_to_use._load_keycloak_config(keycloak_config_filepath)
        assert len(keycloak_config) == expected_size


def test_non_existing_default_file(monkeypatch):
    # When the file at the location determined by TokenFetcherBase.DEFAULT_TOKEN_FILEPATH
    # cannot be loaded (ex: doesn't exist, but the directory does), the user will be
    # prompted to input the configuration values, and the file will be created with them.

    TokenFetcherBase.DEFAULT_TOKEN_FILEPATH = "./tests/tests_data/non_existing_file.yaml"

    assert not os.path.exists(TokenFetcherBase.DEFAULT_TOKEN_FILEPATH)

    prompt_to_response = {
        "Enter the server url:": "a",
        "Enter the client id:": "b",
        "Enter the realm name:": "c",
        "Enter the client password:": None
    }

    def input_response(t):
        return prompt_to_response[t]

    monkeypatch.setattr('builtins.input', input_response)

    ee = TokenFetcherUser._load_keycloak_config(None)

    assert ee == dict(zip(
        TokenFetcherUser.config_keys().keys(),
        prompt_to_response.values()
    ))

    assert os.path.exists(TokenFetcherBase.DEFAULT_TOKEN_FILEPATH)
    os.remove(TokenFetcherBase.DEFAULT_TOKEN_FILEPATH)
