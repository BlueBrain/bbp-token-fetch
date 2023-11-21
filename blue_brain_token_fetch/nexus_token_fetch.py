"""
This CLI allows the fetching and the automatic refreshing of the Nexus token using
Keycloak.
Its value can be written periodically in a file whose path is given in input or be
displayed on the console output as desired.
For more information about Nexus, see https://bluebrainnexus.io/
"""
import os
import time
import logging
import click

from blue_brain_token_fetch.token_fetcher_base import TokenFetcherBase
from blue_brain_token_fetch.token_fetcher_user import TokenFetcherUser
from blue_brain_token_fetch.duration_converter import convert_duration_to_sec
from blue_brain_token_fetch import __version__
from blue_brain_token_fetch.token_fetcher_service import TokenFetcherService

L = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
    help="Username to request the access token",
)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    help="Password to request the access token",
)
@click.option(
    "--output",
    "-o",
    is_flag=True,
    flag_value=False,
    default=True,
    help=(
        "Flag option allowing for 3 distinct outputs:\t\t\t"
        "- {not_given} : By default the fetched token will be written in the file "
        f"located at {TokenFetcherBase.DEFAULT_TOKEN_FILEPATH_LABEL},\t\t\t\t"
        "- {-o/--output} : Providing only the flag will print the token on the "
        "console output,\t"
        "- {-o/--output} {PATH}: If a value (argument 'path') is given as a file path, "
        "the token will be written in this file location,\t"
        "Note: The output file containing the token will have owner read/write access"
    ),
)
@click.argument(
    "path",
    required=False,
    type=click.Path(),
)
@click.option(
    "--refresh-period",
    "-rp",
    default="15",
    help=(
        "Duration of the period between which the token will be written in the file. "
        "It can be expressed as number of seconds or by using time unit : "
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
        "before it is stopped. It can be expressed as number of seconds or by using "
        "time unit : '{float}{time unit}'.\t\t\t\t"
        "Available time unit are :\t\t\t\t\t "
        "- ['s', 'sec', 'secs', 'second', 'seconds'] for seconds, \t\t\t\t\t\t"
        "- ['m', 'min', 'mins', 'minute', 'minutes'] for minutes, \t\t\t\t\t\t\t"
        "- ['h', 'hr', 'hrs', 'hour', 'hours'] for hours, "
        "- ['d', 'day', 'days'] for days. \t\t\t"
        "Ex: '-rp 30' '-rp 30sec', '-rp 0.5min', '-rp 0.1hour'"
    ),
)
@click.option(
    "--keycloak-config-file",
    "-kcf",
    type=click.Path(exists=True),
    help=(
        "The path to the yaml file containing the configuration to create the "
        "keycloak instance. If not provided, it will search in your $HOME directory "
        f"for a '{TokenFetcherBase.DEFAULT_TOKEN_FILEPATH}' file "
        "containing the keycloak configuration.\t\tIf this file does not exist or the "
        "configuration inside is wrong, the configuration will be prompt in the "
        "console output and saved in the $HOME directory under the name: "
        f"'{TokenFetcherBase.DEFAULT_TOKEN_FILEPATH}'."
    ),
)
@click.option("--verbose", "-v", count=True)
@click.option("--service", "-s", count=False,
              help="Whether the account is a service account or not")
def token_fetcher(
    username,
    password,
    output,
    path,
    refresh_period,
    timeout,
    keycloak_config_file,
    verbose,
    service
):
    """
    As a first step it fetches the Nexus access token using Keycloak and the
    username/password values.
    Then it writes it in the given file or displayed it on the console output every
    given 'refresh_period'.\n
    Finally, the process is stopped when the duration reach the value given by the
    'timeout' argument.
    """
    L.setLevel((logging.WARNING, logging.INFO, logging.DEBUG)[min(verbose, 2)])

    if isinstance(password, HiddenPassword):
        password = password.password

    try:
        refresh_period = convert_duration_to_sec(refresh_period)
    except Exception as e:
        L.error(f"Error: {e}")
        exit(1)

    init_cls = TokenFetcherUser if not service else TokenFetcherService
    try:
        my_token_fetcher: TokenFetcherBase = init_cls(username, password, keycloak_config_file)
    except Exception as e:
        L.error(f"Error: {e}")
        exit(1)

    start_time = time.time()
    flag_rp = 0
    flag_to = 0
    flag_console = 0
    while True:

        my_access_token = my_token_fetcher.get_access_token()

        # if refresh period is superior to half of access token duration
        if (
            flag_rp == 0
            and my_token_fetcher.get_access_token_duration() // 2 < refresh_period
        ):
            flag_rp += 1
            L.info(
                f"The refresh period (= {refresh_period} seconds) is greater than the "
                "value of half the access token life span "
                f"(= {my_token_fetcher.get_access_token_duration() // 2:g} seconds)). The "
                "refresh period thus becomes equal to : "
                f"{my_token_fetcher.get_access_token_duration() // 2:g} seconds)."
            )
            refresh_period = my_token_fetcher.get_access_token_duration() // 2

        if timeout:
            if flag_to == 0:
                flag_to += 1
                try:
                    timeout = convert_duration_to_sec(timeout)
                except Exception as e:
                    L.error(f"Error: {e}")
                    exit(1)

                if timeout < refresh_period:
                    L.info(
                        f"The timeout argument (= {timeout:g} seconds) is shorter "
                        f"than the refresh period (= {refresh_period:g} seconds). The "
                        "app will shut down after one refresh period."
                    )

        if path is None and not output:
            if flag_console == 0:
                flag_console += 1
                print(
                    "\n===================== Nexus Token =====================\n\n"
                    f"This access token will be refreshed every {refresh_period:g} "
                    f"seconds:\n\n"
                )
                print(f"{my_access_token}")
            else:
                print(f"\x1B[7A{my_access_token}")
        else:

            output_path = path or TokenFetcherBase.DEFAULT_TOKEN_FILEPATH
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            L.info(
                f"The token will be written in the file '{output_path}' every "
                f"{refresh_period:g} seconds.\r"
            )
            with open(output_path, "w") as f:
                f.write(my_access_token)
            os.chmod(output_path, 0o0600)

        time.sleep(refresh_period)

        if timeout:
            if time.time() > (start_time + timeout):
                L.info("\n> Timeout reached, successfully exit.")
                exit(1)


def start():
    token_fetcher(obj={})


if __name__ == "__main__":
    start()
