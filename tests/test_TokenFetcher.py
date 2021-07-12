import pytest
from pathlib import Path

from blue_brain_token_fetch.Token_refresher import TokenFetcher

TEST_PATH = Path(Path(__file__).parent.parent)


def test_TokenFetcher():

    # KeycloakAuthenticationError
    username = "username"
    password = "password"
    keycloak_config_file = Path(
        Path(__file__).parent.parent, "configuration_files", "keycloack_config.yaml"
    )

    with pytest.raises(SystemExit) as e:
        TokenFetcher(
            username,
            password,
            keycloak_config_file,
        )
    assert e.value.code == 1

    # TypeError
    keycloak_config_file = Path(
        Path(__file__).parent, "tests_data", "empty_keycloack_config.yaml"
    )

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
