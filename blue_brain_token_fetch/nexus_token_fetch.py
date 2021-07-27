"""
This CLI allows the fetching and the automatic refreshing of the Nexus token using 
Keycloak.
Its value can be written periodically in a file whose path is given in input or be 
displayed on the console output as desired.
For more informations about Nexus, see https://bluebrainnexus.io/
"""
import os
import click
import time
import yaml
from blue_brain_token_fetch.Token_refresher import TokenFetcher
from blue_brain_token_fetch.duration_converter import convert_duration_to_sec
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
    show_default=f"Username detected by whoami : {os.environ.get('USER', '')}",
    help="Username required to request the access token",
)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    help="Password required to request the access token",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=f"{os.environ.get('HOME', '')}/Token",
    help=(
        "Path to the text file which will contain the token value.\nThis argument "
        "The default location is $HOME/Token. The output file containing the token "
        "will have owner read/write access"
    ),
)
# backup solution to have 3 output options until click is updated to 8.0.2 :
@click.option(
    "--console",
    is_flag=True,
    expose_value=True,
    prompt=("Do you want the token to be printed on the console ?"),
)
@click.option(
    "--refresh-period",
    "-rp",
    default="15",
    help=(
        "Duration of the period between which the token will be written in the file. "
        "It can be expressed as number of seconds or using time unit : "
        "'{float}{time unit}'.\t\t\t\t "
        "Available time unit are :\t\t\t\t\t "
        "- ['s', 'sec', 'secs', 'second', 'seconds'] for seconds, \t\t\t\t\t\t"
        "- ['m', 'min', 'mins', 'minute', 'minutes'] for minutes, \t\t\t\t\t\t\t"
        "- ['h', 'hr', 'hrs', 'hour', 'hours'] for hours, "
        "- ['d', 'day', 'days'] for days. \t\t\t"
        "Ex: '-rp 30' '-rp 30sec', '-rp 0.5min', '-rp 0.1hour'"
    ),
)
@click.option(
    "--timeout",
    "-to",
    help=(
        "Duration corresponding to the life span to be applied to the application "
        "before it is stopped. It can be expressed as number of seconds or using time "
        "unit : '{float}{time unit}'.\t\t\t\t"
        "Available time unit are :\t\t\t\t\t "
        "- ['s', 'sec', 'secs', 'second', 'seconds'] for seconds, \t\t\t\t\t\t"
        "- ['m', 'min', 'mins', 'minute', 'minutes'] for minutes, \t\t\t\t\t\t\t"
        "- ['h', 'hr', 'hrs', 'hour', 'hours'] for hours, "
        "- ['d', 'day', 'days'] for days. \t\t\t"
        "Ex: '-rp 30' '-rp 30sec', '-rp 0.5min', '-rp 0.1hour'"
    ),
)
def token_fetcher(
    username,
    password,
    output,
    console,
    refresh_period,
    timeout,
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

    refresh_period = convert_duration_to_sec(refresh_period)

    keycloak_config_file = f"{os.environ.get('HOME', '')}/keycloack_config.yaml"
    if (
        not os.path.exists(keycloak_config_file)
        or os.path.getsize(keycloak_config_file) == 0
    ):
        print(
            f"Keycloak configuration file not found at '{keycloak_config_file}'. This "
            "latter will be created with the following given configuration :"
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

    myTokenFetcher = TokenFetcher(username, password, keycloak_config_file)

    start_time = time.time()
    flag_rp = 0
    flag_to = 0
    while True:

        myAccessToken = myTokenFetcher.getAccessToken()

        if console:
            print("\033[H\033[J")
            print("===================== Nexus Token =====================")
            print(
                f"This access token will be refreshed every {refresh_period:g} seconds "
                ": \n"
            )
            print(myAccessToken)
        else:
            print(
                f"The token will be written in the file '{output}' every "
                f"{refresh_period:g} seconds."
            )
            with open(output, "w") as f:
                f.write(myAccessToken)
            os.chmod(output, 0o0600)

        # if refresh period is superior to half of access token duration
        if (
            flag_rp == 0
            and myTokenFetcher.getAccessTokenDuration() // 2 < refresh_period
        ):
            flag_rp += 1
            print(
                f"The refresh period (= {refresh_period} seconds) is greater than the "
                "value of half the access token life span "
                f"(= {myTokenFetcher.getAccessTokenDuration()//2:g} seconds)). The "
                "refresh period thus becomes equal to : "
                f"{myTokenFetcher.getAccessTokenDuration()//2:g} seconds)."
            ),
            refresh_period = myTokenFetcher.getAccessTokenDuration() // 2

        time.sleep(refresh_period)

        if timeout:
            if flag_to == 0:
                flag_to += 1
                timeout = convert_duration_to_sec(timeout)

                if timeout < refresh_period:
                    print(
                        f"The timeout argument (= {timeout:g} seconds) is shorter "
                        f"than the refresh period (= {refresh_period:g} seconds). The "
                        "app will shut down after one refresh period."
                    ),
            if time.time() > (start_time + timeout):
                print("> Timeout reached, successfully exit.")
                exit(1)


def start():
    token_fetcher(obj={})


if __name__ == "__main__":
    start()
