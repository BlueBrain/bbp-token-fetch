## Description
This CLI allows the fetching and the automatic refreshing of the Nexus token using Keycloak. Its value can be written periodically in a file whose path is given in input or be displayed on the console output as desired.
The CLI is based on the class TokenFetcher that is in charge of the token fetching and refreshing. If being imported as a library, two public methods of a TokenFetcher object makes possible to get a fresh Nexus access token and to get its life duration.

For more informations about Nexus, see https://bluebrainnexus.io/

## Source
You can find the source of this module here: [https://bbpgitlab.epfl.ch/dke/users/nabilalibou/blue_brain_nexus_token_fetch]

## Install
Clone the repository:
```
git clone https://bbpgitlab.epfl.ch/dke/users/nabilalibou/blue_brain_nexus_token_fetch.git
```

And install with pip:
```
cd blue_brain_nexus_token_fetch
pip install .
```
From now on, the executable **blue-brain-token-fetch** is in your PATH.

## CLI arguments
- **--username** - [Prompt] Gaspard identifiant to access Nexus services. Default is the environmental variable USER.
- **--password** - [Prompt] Gaspard identifiant to access Nexus services. Default is the environmental variable PASSWORD (if existing).
- **--token-file** - [File path] Path to the text file which will contain the token value.
- **--refresh-period 15** - [int range (1, 15)] Duration of the period (secondes) between which the token will be written in the file.
- **--timeout** - [int] Duration (secondes) corresponding to the life span to be applied to the application before it is stopped.
- **--keycloak-config-file /configuration_files/keycloack_config.yaml** - [Path] The path to the yaml file containing the configuration to create the keycloak instance.

## Examples
- Print to the console output a fresh 'access token' continously :
```
blue-brain-token-fetch
```

- Write every 10 seconds a fresh 'access token' into the token file before exiting after 1 hour:
```
blue-brain-token-fetch --token-file ./token.txt \
              	       --refresh-period 10 \
                       --timeout 3600 \
```
- If imported in a script:
```
myTokenFetcher = TokenFetcher(username, password, keycloak_config_file) #instantiate
myAccessToken = myTokenFetcher.getAccessToken() # fetch a fresh access token
Acess_token_duration = myTokenFetcher.getAccessTokenDuration() # get the access token duration
```
## Maintainers
This module was originally created by Nabil ALIBOU, DKE (nabil.alibou@epfl.ch).
