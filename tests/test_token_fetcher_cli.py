from pathlib import Path
from click.testing import CliRunner

from blue_brain_token_fetch.nexus_token_fetch import token_fetcher

TEST_PATH = Path(Path(__file__).parent.parent)


def test_token_fetcher_cli():

    username = "username"
    password = "password"

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            token_fetcher,
            [
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 1
