"""This class allows the fetching and the automatic refreshing of the Nexus token using 
Keycloak.
It contains 2 public methods to get a fresh Nexus access token and to get its life 
duration.
For more informations about Nexus, see https://bluebrainnexus.io/
"""
import os
import yaml
import time
import getpass
import threading
import logging
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError, KeycloakAuthenticationError

L = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TokenFetcher:
    """
    A class to represent a Token Fetcher.

    Attributes
    ----------
    username : str
        gaspard identifiant to access the Nexus token
    password : str
        gaspard identifiant to access the Nexus token
    keycloak_config_file : Path
        Path of the keycloack configuration file

    Methods
    -------
    getAccessToken():
        Return a fresh Nexus access token.
    getAccessTokenDuration():
        Return the access token life duration.
    """

    def __init__(self, username=None, password=None, keycloak_config_file=None):
        """
        Constructs all the necessary attributes for the TokenFetcher object. After
        that, call the appropried method launching the perpetual token refreshing
        depending on whether identifiers have been given or not.

        Parameters
        ----------
            username : str
                gaspard identifiant to access the Nexus token
            password : str
                gaspard identifiant to access the Nexus token
            keycloak_config_file : str (file path)
                Path of the keycloack configuration file
        """

        self._keycloak_openid = None
        self._keycloak_payload = None
        self._refresh_token = None
        self._refresh_token_duration = None

        if username and password:
            self.init_no_prompt(username, password, keycloak_config_file)
        else:
            self.init_with_prompt(keycloak_config_file)

    def init_with_prompt(self, keycloak_config_file):
        """
        Promt username, password and keycloak instance configuration parameters and 
        initialise the keycloack instance and launch the perpetual refreshing of the 
        refresh token.

        Parameters
        ----------
            keycloak_config_file : str (file path)
                Path of the keycloack configuration file
        """

        detected_user = getpass.getuser()
        username = input(f"Username [{detected_user}]: ")
        if not username:
            username = detected_user
        password = getpass.getpass()

        server_url, client_id, realm_name, save_config = self._return_keycloak_config(
            keycloak_config_file
        )
        self._fetchTokens(
            username, password, server_url, client_id, realm_name, save_config
        )
        self._refreshPerpetualy(username, password)

    def init_no_prompt(self, username, password, keycloak_config_file):
        """
        Initialise the keycloack instance and launch the perpetual refreshing of the
        refresh token.

        Parameters
        ----------
            username : str
                gaspard identifiant to access the Nexus token
            password : str
                gaspard identifiant to access the Nexus token
            keycloak_config_file : str (file path)
                Path of the keycloack configuration file
        """
        server_url, client_id, realm_name, save_config = self._return_keycloak_config(
            keycloak_config_file
        )
        self._fetchTokens(
            username, password, server_url, client_id, realm_name, save_config
        )
        self._refreshPerpetualy(username, password)

    def _return_keycloak_config(self, keycloak_config_file=None, save_config=True):

        if keycloak_config_file:
            try:
                server_url, client_id, realm_name = self._read_keycloak_config_file(
                    keycloak_config_file
                )
                save_config = False
            except Exception as e:
                L.error(
                    f"Error when extracting the keycloak configuration from the input"
                    f"'{keycloak_config_file}'. {e}."
                )
                exit(1)
        elif os.path.exists(
            f"{os.environ.get('HOME', '')}/.token_fetch/keycloack_config.yaml"
        ):
            L.info(
                "Keycloak configuration file found in $HOME/.token_fetch directory : "
                f"'{os.environ.get('HOME', '')}/.token_fetch/keycloack_config.yaml'"
            )
            try:
                server_url, client_id, realm_name = self._read_keycloak_config_file(
                    f"{os.environ.get('HOME', '')}/.token_fetch/keycloack_config.yaml"
                )
                save_config = False

            except Exception as e:
                L.info(
                    f"Error when extracting the keycloak configuration from  "
                    f"'{os.environ.get('HOME', '')}/.token_fetch/keycloack_config.yaml'"
                    f". {e}.\nThis latter will be reset with the new given "
                    "configuration:"
                )
                server_url = input("Enter the server url : ")
                client_id = input("Enter the client id : ")
                realm_name = input("Enter the realm name : ")
        else:
            L.info(
                "No keycloak configuration file given in input or found in "
                "$HOME/.token_fetch directory. A new keycloak configuration file will "
                "be created with the given configuration:\n> Please enter the new "
                "configuration to be saved >"
            )
            server_url = input("Enter the server url : ")
            client_id = input("Enter the client id : ")
            realm_name = input("Enter the realm name : ")

        return server_url, client_id, realm_name, save_config

    def _read_keycloak_config_file(self, keycloak_config_file):

        try:
            config_file = open(keycloak_config_file)
            config_content = yaml.safe_load(config_file.read().strip())
            config_file.close()
            return (
                config_content["SERVER_URL"],
                config_content["CLIENT_ID"],
                config_content["REALM_NAME"],
            )
        except OSError as error:
            raise OSError(f"⚠️  OSError. {error}")
        except KeyError as error:
            raise KeyError(
                f"⚠️  KeyError {error}. The keycloak instance is configured using the "
                "keys 'SERVER_URL', 'CLIENT_ID' and 'REALM_NAME' extracted from the "
                "keycloack configuration file"
            )
        except TypeError as error:
            raise TypeError(
                f"⚠️  TypeError {error}. The keys 'SERVER_URL', 'CLIENT_ID' and "
                "'REALM_NAME' are missing in keycloack configuration file"
            )

    def _periodically_refresh_token(self):
        """
        Periodically refresh the 'refresh token' every half of its life duration.
        """
        while True:
            self._refresh_token = self._keycloak_openid.refresh_token(
                self._refresh_token
            )["refresh_token"]
            time.sleep(self._refresh_token_duration // 2)  # 14400

    def _refreshPerpetualy(self, username, password):
        """
        Launch the thread encapsulating '_periodically_refresh_token()'.

        Parameters
        ----------
            username : str
                gaspard identifiant to access the Nexus token
            password : str
                gaspard identifiant to access the Nexus token
        """
        tokenRefreshingThread = threading.Thread(
            target=self._periodically_refresh_token, daemon=True
        )
        tokenRefreshingThread.start()

    def _fetchTokens(
        self, username, password, server_url, client_id, realm_name, save_config=True
    ):
        """
        Configure a Keycloack instance using the configuration file and the
        identifiants then fetch a refresh token and its life duration.

        Parameters
        ----------
            username : str
                gaspard identifiant to access the Nexus token
            password : str
                gaspard identifiant to access the Nexus token
            server_url : str
                url of the  server (keycloak configuration)
            client_id : str
                client id (keycloak configuration)
            realm_name : str
                name of the realm (keycloak configuration)
            save_config : boolean
                Save the given configuration in the keycloak configuration file or not
        """
        try:
            self._keycloak_openid = KeycloakOpenID(
                server_url=server_url,
                client_id=client_id,
                realm_name=realm_name,
            )

            self._keycloak_payload = self._keycloak_openid.token(username, password)
            del password

            self._refresh_token = self._keycloak_payload["refresh_token"]
            self._refresh_token_duration = self._keycloak_payload["refresh_expires_in"]

            config_dict = {
                "SERVER_URL": server_url,
                "CLIENT_ID": client_id,
                "REALM_NAME": realm_name,
            }

            if save_config:
                try:
                    os.makedirs(f"{os.environ.get('HOME', '')}/.token_fetch")
                except FileExistsError:
                    pass
                keycloak_config_file = (
                    f"{os.environ.get('HOME', '')}/.token_fetch/keycloack_config.yaml"
                )
                with open(f"{keycloak_config_file}", "w") as f:
                    yaml.dump(config_dict, f)
                L.info(
                    "This configuration will be saved in the file "
                    "'{keycloak_config_file}' that will be reused next time."
                )
        except KeycloakError as error:
            L.error(f"⚠️  KeycloakError. Authentication failed, {error}.")
            exit(1)
        except KeycloakAuthenticationError as error:
            L.error(f"⚠️  KeycloakAuthenticationError. Authentication failed, {error}")
            exit(1)

    def getAccessToken(self):

        return self._keycloak_openid.refresh_token(self._refresh_token)["access_token"]

    def getAccessTokenDuration(self):

        return self._keycloak_payload["expires_in"]
