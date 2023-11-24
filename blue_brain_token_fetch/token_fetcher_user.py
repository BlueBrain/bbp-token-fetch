"""This class allows the fetching and the automatic refreshing of the Nexus token using
Keycloak.
It contains 2 public methods to get a fresh Nexus access token and to get its life
duration.
For more information about Nexus, see https://bluebrainnexus.io/
"""
import time
import threading
from typing import Tuple, Dict

from keycloak import KeycloakOpenID

from blue_brain_token_fetch.token_fetcher_base import TokenFetcherBase


class TokenFetcherUser(TokenFetcherBase):

    _refresh_token = None
    _refresh_token_duration = None

    @classmethod
    def config_keys(cls):
        return ["SERVER_URL", "CLIENT_ID", "REALM_NAME"]

    def get_access_token(self):
        return self._keycloak_openid.refresh_token(self._refresh_token)["access_token"]

    def _refresh_perpetually(self):
        """
        Launch the thread encapsulating '_periodically_refresh_token()'.
        """
        token_refreshing_thread = threading.Thread(
            target=self._periodically_refresh_token, daemon=True
        )
        token_refreshing_thread.start()

    def _periodically_refresh_token(self):
        """
        Periodically refresh the 'refresh token' every half of its life duration.
        """
        while True:
            self._refresh_token = self._keycloak_openid.refresh_token(
                self._refresh_token
            )["refresh_token"]
            time.sleep(self._refresh_token_duration // 2)  # 14400

    def _get_keycloak_instance_and_payload(
            self, username, password, keycloak_config
    ) -> Tuple[KeycloakOpenID, Dict]:

        instance = KeycloakOpenID(
            server_url=keycloak_config["SERVER_URL"],
            client_id=keycloak_config["CLIENT_ID"],
            realm_name=keycloak_config["REALM_NAME"],
        )

        payload = instance.token(username, password)
        self._refresh_token = payload["refresh_token"]
        self._refresh_token_duration = payload["refresh_expires_in"]
        return instance, payload