""" 
Fetch and refresh of the Nexus token using Keycloak and write its value periodically in the file whose path is given is input.
For more informations about Nexus, see https://bluebrainnexus.io/
"""
import os
import click
from blue_brain_token_fetch.periodic_token_fetching import token_fetch, token_periodic_call
from blue_brain_token_fetch import __version__


class HiddenPassword(object):
    def __init__(self, password=''):
        self.password = password
    def __str__(self):
        return '*' * 4 # no informations is inferable 


@click.command()
@click.version_option(__version__)
@click.option(
    "--token-file",
    required=True,
    help="Path to the text file which will contain the token value",
)
@click.option(
    '--username', prompt=True,
    default=lambda: os.environ.get('USER', ''), 
    show_default=f"Detected Username : {os.environ.get('USER', '')}"
)
@click.option(
    "--password", prompt=True, hide_input=True,
    default=lambda: HiddenPassword(os.environ.get('PASSWORD', '')),
)
def fetch_token(token_file, username, password):
    """
    As a first step it fetches the Nexus access token, its duration and the refresh token using 
    Keycloak and the username/password values.\n
    Then refresh it periodically (every half of the access token duration) and write it in the 
    given input file.
    """
    if isinstance(password, HiddenPassword):
        password = password.password
    
    keycloak_openid, refresh_token, token_duration = token_fetch(username, password)
    del password
    token_periodic_call(keycloak_openid, refresh_token, token_duration, token_file)


def start():
    fetch_token(obj={})


if __name__ == "__main__":
    start()
