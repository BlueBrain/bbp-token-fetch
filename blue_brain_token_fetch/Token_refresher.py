import sys
import yaml
import time
import getpass
import threading
from pathlib import Path
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError


class TokenFetcher:
    def __init__(
        self,
        username=None,
        password=None,
        timeout=None,
        keycloak_config_file=Path(
            Path(__file__).parent, "configuration_files", "keycloack_config.yaml"
        ),
    ):

        self._keycloak_openid = None
        self._keycloak_payload = None
        self._refresh_token = None
        self._refresh_token_duration = None

        if username and password:
            self.init_no_prompt(username, password, timeout, keycloak_config_file)
        else:
            self.init_with_prompt(timeout, keycloak_config_file)

    def init_with_prompt(self, timeout, keycloak_config_file):

        detected_user = getpass.getuser()
        username = input(f"Username [{detected_user}]: ")
        if not username:
            username = detected_user
        password = getpass.getpass()

        self._fetchTokens(username, password, keycloak_config_file)
        self._refreshPerpetualy(username, password, timeout)

    def init_no_prompt(self, username, password, timeout, keycloak_config_file):

        self._fetchTokens(username, password, keycloak_config_file)
        self._refreshPerpetualy(username, password, timeout)  # sure?

    def _periodically_refresh_token(self):

        while True:
            self._refresh_token = self._keycloak_openid.refresh_token(
                self._refresh_token
            )["refresh_token"]
            time.sleep(self._refresh_token_duration // 2)  # 28800

    def _refreshPerpetualy(self, username, password, timeout):

        tokenRefreshingThread = threading.Thread(
            target=self._periodically_refresh_token, daemon=True
        )
        tokenRefreshingThread.start()

    def _fetchTokens(self, username, password, keycloak_config_file):

        try:
            config_file = open(keycloak_config_file)
            config_content = yaml.safe_load(config_file.read().strip())
            config_file.close()
            self._keycloak_openid = KeycloakOpenID(
                server_url=config_content["SERVER_URL"],
                client_id=config_content["CLIENT_ID"],
                realm_name=config_content["REALM_NAME"],
            )  # verify=True?

            self._keycloak_payload = self._keycloak_openid.token(username, password)
            del password

            self._refresh_token = self._keycloak_payload["refresh_token"]
            self._refresh_token_duration = self._keycloak_payload["refresh_expires_in"]

        except OSError as error:
            print(f"OSError: {error}.")
            exit(1)
        except KeyError as error:
            print(
                f"KeyError: {error}. The keys 'SERVER_URL', 'CLIENT_ID' and 'REALM_NAME' are "
                "missing in keycloack configuration file"
            )
            exit(1)
        except KeycloakError as error:
            print(f"Authentication failed: {error}")
            exit(1)

    def getAccessToken(self):

        return self._keycloak_openid.refresh_token(self._refresh_token)["access_token"]

    def getAccessTokenDuration(self):

        return self._keycloak_payload["expires_in"]
