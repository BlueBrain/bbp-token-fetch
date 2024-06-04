"""This class allows the fetching and the automatic refreshing of the Nexus token using
Keycloak.
It contains 2 public methods to get a fresh Nexus access token and to get its life
duration.
For more information about Nexus, see https://bluebrainnexus.io/
"""
from typing import Tuple, Dict

from keycloak import KeycloakOpenID
from blue_brain_token_fetch.token_fetcher_base import TokenFetcherBase


class TokenFetcherService(TokenFetcherBase):

    def get_access_token(self):
        return self._keycloak_openid.token(grant_type="client_credentials")["access_token"]

    @classmethod
    def config_keys(cls) -> Dict[str, bool]:
        return {"SERVER_URL": True, "REALM_NAME": True}

    def _refresh_perpetually(self):
        pass

    def _get_keycloak_instance_and_payload(
            self, username, password, keycloak_config
    ) -> Tuple[KeycloakOpenID, Dict]:

        instance = KeycloakOpenID(
            server_url=keycloak_config["SERVER_URL"],
            realm_name=keycloak_config["REALM_NAME"],
            client_id=username,
            client_secret_key=password,
        )
        payload = instance.token(grant_type="client_credentials")

        return instance, payload
