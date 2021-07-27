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
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError, KeycloakAuthenticationError


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
            keycloak_config_file : int
                Path of the keycloack configuration file
        """

        self._keycloak_openid = None
        self._keycloak_payload = None
        self._refresh_token = None
        self._refresh_token_duration = None

        if username and password:
            self.init_no_prompt(username, password, keycloak_config_file)
        else:
            self.init_with_prompt()

    def init_with_prompt(self):
        """
        Promt username, password and keycloak instance configuration parameters and "
        initialise the keycloack instance and launch the perpetual refreshing of the "
        "refresh token.
        """

        detected_user = getpass.getuser()
        username = input(f"Username [{detected_user}]: ")
        if not username:
            username = detected_user
        password = getpass.getpass()

        keycloak_config_file = f"{os.environ.get('HOME', '')}/keycloack_config.yaml"
        if (
            not os.path.exists(keycloak_config_file)
            or os.path.getsize(keycloak_config_file) == 0
        ):
            print(
                f"Keycloak configuration file not found at '{keycloak_config_file}'. "
                "This latter will be created with the following given configuration :"
            )
            SERVER_URL = input("Enter the server url : ")
            CLIENT_ID = input("Enter the client id : ")
            REALM_NAME = input("Enter the realm name : ")
            config_dict = {
                "SERVER_URL": SERVER_URL,
                "CLIENT_ID": CLIENT_ID,
                "REALM_NAME": REALM_NAME,
            }
            print(
                "This configuration will be saved in the file '{keycloak_config_file}' "
                "that will be reused next time."
            )
            with open(keycloak_config_file, "w") as f:
                yaml.dump(config_dict, f)

        self._fetchTokens(username, password, keycloak_config_file)
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
            keycloak_config_file : int
                Path of the keycloack configuration file
        """
        self._fetchTokens(username, password, keycloak_config_file)
        self._refreshPerpetualy(username, password)

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

    def _fetchTokens(self, username, password, keycloak_config_file):
        """
        Configure a Keycloack instance using the configuration file and the
        identifiants then fetch a refresh token and its life duration.

        Parameters
        ----------
            username : str
                gaspard identifiant to access the Nexus token
            password : str
                gaspard identifiant to access the Nexus token
            keycloak_config_file : int
                Path of the keycloack configuration file
        """
        try:
            config_file = open(keycloak_config_file)
            config_content = yaml.safe_load(config_file.read().strip())
            config_file.close()
            self._keycloak_openid = KeycloakOpenID(
                server_url=config_content["SERVER_URL"],
                client_id=config_content["CLIENT_ID"],
                realm_name=config_content["REALM_NAME"],
            )

            self._keycloak_payload = self._keycloak_openid.token(username, password)
            del password

            self._refresh_token = self._keycloak_payload["refresh_token"]
            self._refresh_token_duration = self._keycloak_payload["refresh_expires_in"]

        except OSError as error:
            print(f"OSError: {error}.")
            exit(1)
        except KeyError as error:
            print(
                f"KeyError: {error}. The keycloak instance is configured using the "
                "keys 'SERVER_URL', 'CLIENT_ID' and 'REALM_NAME' extracted from the "
                "keycloack configuration file"
            )
            exit(1)
        except TypeError as error:
            print(
                f"TypeError: {error}. The keys 'SERVER_URL', 'CLIENT_ID' and "
                "'REALM_NAME' are missing in keycloack configuration file"
            )
            exit(1)
        except KeycloakError as error:
            print(f"Authentication failed. {error}.")
            with open(keycloak_config_file, "w") as f:
                f.truncate()
            print("> Content of the keycloak configuration file has been reset.")
            exit(1)
        except KeycloakAuthenticationError as error:
            print(f"Authentication failed. {error}")
            exit(1)

    def getAccessToken(self):

        return self._keycloak_openid.refresh_token(self._refresh_token)["access_token"]

    def getAccessTokenDuration(self):

        return self._keycloak_payload["expires_in"]
