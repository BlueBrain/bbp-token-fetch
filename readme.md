## Description
This CLI allows the fetching and the automatic refreshing of the Nexus token using Keycloak. Its value can be written periodically in a file whose path is given in input or be displayed on the console output as desired.
The CLI is based on the class TokenFetcher that is in charge of the token fetching and refreshing. If being imported as a library, two public methods of a TokenFetcher object makes possible to get a fresh Nexus access token and to get its life duration.

For more informations about Nexus, see https://bluebrainnexus.io/

## Source
You can find the source of this module here: [https://bbpgitlab.epfl.ch/dke/apps/blue_brain_nexus_token_fetch]

## Install
Clone the repository:
```
git clone https://bbpgitlab.epfl.ch/dke/apps/blue_brain_nexus_token_fetch.git
```

And install with pip:
```
cd blue_brain_nexus_token_fetch
pip install .
```
From now on, the executable **blue-brain-token-fetch** is in your PATH.

## CLI arguments
- **--username** - [Prompt] Username to request the access token. Default is the username detected by whoami (environmental variable $USER).
- **--password** - [Prompt] Password to request the access token.
- **--output / -o** - [Flag] Flag option allowing for 3 distinct outputs:
  - {not_given} : By default the fetched token will be written in the file located at
    $HOME/.token_fetch/Token,
  - {-o/--output} : Providing only the flag will print the token on the console output,
  - {-o/--output} {PATH}: If a value (argument 'path') is given as a file path, the token
    will be written in this file location,
Note: The output file containing the token will have owner read/write access.
- **path** - [File path] Path to the eventual output token file.
- **--refresh-period / -rp** - [default 15] Duration of the period between which the token
will be written in the file. It can be expressed as number of seconds or by using time unit : '{float}{time unit}'.Available time unit are :
  - ['s', 'sec', 'secs', 'second', 'seconds'] for seconds,
  - ['m', 'min', 'mins', 'minute', 'minutes'] for minutes,
  - ['h', 'hr', 'hrs', 'hour', 'hours'] for hours,
  - ['d', 'day', 'days'] for days.
Ex: '-rp 30' '-rp 30sec', '-rp 0.5min', '-rp 0.1hour'
- **--timeout / -to** - "Duration corresponding to the life span to be applied to the application before it is stopped. It can be expressed as number of seconds or by using time unit : '{float}{time unit}'. Available time unit are :
  - ['s', 'sec', 'secs', 'second', 'seconds'] for seconds,
  - ['m', 'min', 'mins', 'minute', 'minutes'] for minutes,
  - ['h', 'hr', 'hrs', 'hour', 'hours'] for hours,
  - ['d', 'day', 'days'] for days.
Ex: '-rp 30' '-rp 30sec', '-rp 0.5min', '-rp 0.1hour'
- **--keycloak-config-file / -kcf** - [File Path] The path to the yaml file containing the configuration to create the keycloak instance. If not provided, it will search in your $HOME directory for a '$HOME/.token_fetch/keycloack_config.yaml' file containing the keycloak configuration.If this file does not exist or the configuration inside is wrong, the configuration will be prompt in the console output and saved in the $HOME directory under the name: '$HOME/.token_fetch/keycloack_config.yaml'.

## Examples
- Print to the console output a fresh 'access token' continously :
```
blue-brain-token-fetch
```

- Write every 10 seconds a fresh 'access token' into the token file before exiting after 1 hour:
```
blue-brain-token-fetch -o path ./token.txt \
              	       -rp 10s \
                       -to 1h \
```
Note: If you want to regaining control on the keyboard you can launch the CLI then kill its process then relaunch it in background mode by doing:
```
blue-brain-token-fetch
# ctrl+z
bg
```
- If imported in a script:
```
myTokenFetcher = TokenFetcher(username, password, keycloak_config_file) #instantiate
myAccessToken = myTokenFetcher.getAccessToken() # fetch a fresh access token
Acess_token_duration = myTokenFetcher.getAccessTokenDuration() # get the access token duration
```
## Maintainers
This module was originally created by Nabil ALIBOU, DKE (nabil.alibou@epfl.ch).
