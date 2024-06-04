"""This class allows the fetching and the automatic refreshing of the Nexus token using
Keycloak.
It contains 2 public methods to get a fresh Nexus access token and to get its life
duration.
For more information about Nexus, see https://bluebrainnexus.io/
"""
import os
from abc import abstractmethod, ABC
from typing import Dict, Tuple, List

import getpass
import logging
import yaml

from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError, KeycloakAuthenticationError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TokenFetcherBase(ABC):
    """
    A class to represent a Token Fetcher.

    Attributes
    ----------
    username : str
        gaspard identifier to access the Nexus token
    password : str
        gaspard identifier to access the Nexus token
    keycloak_config_file : Path
        Path of the keycloak configuration file

    Methods
    -------
    get_access_token():
        Return a fresh Nexus access token.
    get_access_token_duration():
        Return the access token life duration.
    """

    DEFAULT_CONFIG_FILENAME = "keycloack_config.yaml"
    DEFAULT_TOKEN_FILENAME = "Token"
    DEFAULT_SUBDIRECTORY = ".token_fetch"

    DEFAULT_DIRECTORY = os.path.join(os.environ.get('HOME', ''), DEFAULT_SUBDIRECTORY)
    DEFAULT_CONFIG_FILEPATH = os.path.join(DEFAULT_DIRECTORY, DEFAULT_CONFIG_FILENAME)
    DEFAULT_TOKEN_FILEPATH = os.path.join(DEFAULT_DIRECTORY, DEFAULT_TOKEN_FILENAME)

    DEFAULT_DIRECTORY_LABEL = os.path.join("$HOME", DEFAULT_SUBDIRECTORY)
    DEFAULT_CONFIG_FILEPATH_LABEL = os.path.join(DEFAULT_DIRECTORY, DEFAULT_CONFIG_FILENAME)
    DEFAULT_TOKEN_FILEPATH_LABEL = os.path.join(DEFAULT_DIRECTORY, DEFAULT_TOKEN_FILENAME)

    def __init__(self, username=None, password=None, keycloak_config_file=None):
        """
        Constructs all the necessary attributes for the TokenFetcher object. After
        that, call the appropriate method launching the perpetual token refreshing
        depending on whether identifiers have been given or not.

        Parameters
        ----------
            username : str
                gaspard identifier to access the Nexus token
            password : str
                gaspard identifier to access the Nexus token
            keycloak_config_file : str (file path)
                Path of the keycloak configuration file
        """

        username, password = self._get_credentials(username, password)
        keycloak_config = self._load_keycloak_config(keycloak_config_file)

        try:
            self._keycloak_openid, self._keycloak_payload = self._get_keycloak_instance_and_payload(
                username, password, keycloak_config
            )

            self._interrupt_callback = self._refresh_perpetually()

            del password

        except (KeycloakAuthenticationError, KeycloakError) as error:
            logger.error("⚠️ %s. Authentication failed, %s", error.__class__.__name__, error)
            raise error

    @abstractmethod
    def _refresh_perpetually(self):
        ...

    @classmethod
    @abstractmethod
    def config_keys(cls) -> Dict[str, bool]:
        """
        Keys to be retrieved from the configuration file, and whether they are mandatory or not
        """
        pass

    @classmethod
    def _load_keycloak_config(cls, keycloak_config_file=None):

        if keycloak_config_file:
            file_name = keycloak_config_file
        else:
            file_name = TokenFetcherBase.DEFAULT_TOKEN_FILEPATH
            logger.info('Keycloak configuration file found : %s', file_name)

        try:
            if not os.path.exists(file_name):
                raise FileNotFoundError(f"⚠️  FileNotFoundError. Cannot find file {file_name}")
            try:
                with open(file_name) as config_file:
                    config_content = yaml.safe_load(config_file.read().strip())
            except OSError as error:
                raise OSError(f"⚠️  OSError. {error}") from error

            if config_content is None:
                raise ValueError("⚠️  Keycloak configuration file is empty")

            try:
                [config_content[key] for key, mandatory in cls.config_keys().items() if mandatory]
            except KeyError as error:
                raise KeyError(
                    f"⚠️  KeyError {error}. Mandatory keys in the keycloak configuration file are"
                    f" {cls.config_keys()}"
                ) from error

            return config_content

        except Exception as e:

            logger.info(
                "Error when extracting the keycloak configuration from %s. %s.", file_name, e
            )

            if keycloak_config_file is not None:
                raise e

            logger.info("This latter will be reset with the new given configuration:")

            # only accept input for default file, not specified keycloak config file
            config_dict = dict(
                (key, input(f"Enter the {key.lower().replace('_', ' ')}:") or None)
                for key in cls.config_keys()
            )

            os.makedirs(os.path.dirname(file_name), exist_ok=True)

            with open(file_name, "w") as f:
                yaml.dump(config_dict, f)

            logger.info(
                "This configuration will be saved in the file %s that will be reused next time.",
                file_name
            )

            return config_dict

    def get_access_token_duration(self):
        return self._keycloak_payload["expires_in"]

    @abstractmethod
    def get_access_token(self):
        pass

    @abstractmethod
    def _get_keycloak_instance_and_payload(
            self, username, password, keycloak_config
    ) -> Tuple[KeycloakOpenID, Dict]:
        pass

    @staticmethod
    def _get_credentials(username: str, password: str) -> Tuple[str, str]:
        if username and password:
            return username, password

        detected_user = getpass.getuser()
        username = input(f"Username [{detected_user}]: ")
        if not username:
            username = detected_user
        password = getpass.getpass()

        return username, password
