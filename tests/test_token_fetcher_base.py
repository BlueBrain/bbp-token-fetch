import pytest
from blue_brain_token_fetch.token_fetcher_user import TokenFetcherUser
from contextlib import nullcontext as does_not_raise

from blue_brain_token_fetch.token_fetcher_base import TokenFetcherBase
from blue_brain_token_fetch.token_fetcher_service import TokenFetcherService
from tests.conftest import SERVICE_CONFIG, REGULAR_CONFIG


@pytest.mark.parametrize("class_to_use, keycloak_config_filepath, expected_size, exception", [
    pytest.param(
        TokenFetcherService, SERVICE_CONFIG, 2, does_not_raise(), id="sa"
    ),
    pytest.param(
        TokenFetcherUser, REGULAR_CONFIG, 3, does_not_raise(), id="non_sa"
    )
])
def test_config_file(class_to_use: TokenFetcherBase, keycloak_config_filepath, expected_size,
                     exception):
    with exception:
        keycloak_config = class_to_use._load_keycloak_config(keycloak_config_filepath)
        assert len(keycloak_config) == expected_size
