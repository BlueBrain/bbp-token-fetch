"""
This CLI allows the fetching and the automatic refreshing of the Nexus token using 
Keycloak. Its value can be written periodically in a file whose path is given in input 
or be displayed on the console output as desired.
For more informations about Nexus, see https://bluebrainnexus.io/
"""
import os
import click
import time
from pathlib import Path
from blue_brain_token_fetch.Token_refresher import TokenFetcher
from blue_brain_token_fetch import __version__


class HiddenPassword(object):
    def __init__(self, password=""):
        self.password = password

    def __str__(self):
        return "*" * 4


@click.command()
@click.version_option(__version__)
@click.option(
    "--username",
    prompt=True,
    default=lambda: os.environ.get("USER", ""),
    show_default=f"Detected Username : {os.environ.get('USER', '')}",
    help="Gaspard identifiant to access Nexus services",
)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    default=lambda: HiddenPassword(os.environ.get("PASSWORD", "")),
    help="Gaspard identifiant to access Nexus services",
)
@click.option(
    "--token-file",
    "-tf",
    type=click.Path(),
    help="Path to the text file which will contain the token value",
)
@click.option(
    "--refresh-period",
    "-rp",
    type=click.IntRange(1, 15),
    default=15,
    help=(
        "Duration of the period (secondes) between which the token will be written "
        "in the file"
    ),
)
@click.option(
    "--timeout",
    "-to",
    type=int,
    help=(
        "Duration (secondes) corresponding to the life span to be applied to the "
        "application before it is stopped"
    ),
)
@click.option(
    "--keycloak-config-file",
    "-kcf",
    type=click.Path(exists=True),
    default=Path(Path(__file__).parent, "configuration_files", "keycloack_config.yaml"),
    help=(
        "The path to the yaml file containing the configuration to create the "
        "keycloak instance"
    ),
)
def token_fetcher(
    username, password, token_file, refresh_period, timeout, keycloak_config_file
):
    """
    As a first step it fetches the Nexus access token using Keycloack and the
    username/password values.
    Then it writes it in the given file or displayed it on the console output every
    given 'refresh_period'.\n
    Finally, the process is stopped when the duration reach the value given by the
    'timeout' argument.
    """
    if isinstance(password, HiddenPassword):
        password = password.password

    myTokenFetcher = TokenFetcher(username, password, keycloak_config_file)

    start_time = time.time()
    print_flag_a = 0
    print_flag_b = 0
    while True:

        myAccessToken = myTokenFetcher.getAccessToken()

        if token_file:
            with open(token_file, "w") as f:
                f.write(myAccessToken)
            os.chmod(token_file, 0o0600)
        else:
            print("\033[H\033[J")
            print(myAccessToken)

        if (
            print_flag_a == 0
            and myTokenFetcher.getAccessTokenDuration() < refresh_period
        ):
            print_flag_a += 1
            print(
                f"The access token life span (= "
                "{myTokenFetcher.getAccessTokenDuration()} seconds) is shorter than "
                "the refresh period (= {refresh_period} seconds). The latter thus "
                "becomes equal to {myTokenFetcher.getAccessTokenDuration()} seconds."
            ),
            refresh_period = myTokenFetcher.getAccessTokenDuration()

        if print_flag_b == 0 and timeout and timeout < refresh_period:
            print_flag_b += 1
            print(
                f"The timeout argument (= {timeout} seconds) is shorter than the "
                "refresh period (= {refresh_period} seconds). The app will shut down "
                "after one refresh period."
            ),

        time.sleep(refresh_period)

        if timeout:
            if time.time() > (start_time + timeout):
                print("> Timeout reached, successfully exit.")
                exit(1)


def start():
    token_fetcher(obj={})


if __name__ == "__main__":
    start()
