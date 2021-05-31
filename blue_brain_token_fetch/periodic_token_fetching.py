"""
Functions to allowing the fetching and periodic refreshing of the Nexus token using Keycloak. Its 
value is writed periodically in the file given in input.
For more informations about Nexus, see https://bluebrainnexus.io/
"""
import time
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError


def _token_refresh(keycloak_openid, refresh_token, token_file):
    access_token = keycloak_openid.refresh_token(refresh_token)['access_token']
    refresh_token = keycloak_openid.refresh_token(refresh_token)['refresh_token']
    with open(token_file, 'w') as f:
        f.write(access_token)
    return refresh_token


def token_fetch(username, password):

    refresh_token = None
    token_duration = None

    server_url = 'https://bbpauth.epfl.ch/auth/'
    client_id = 'bbp-atlas-pipeline'
    realm_name = 'BBP'
    
    try:
        keycloak_openid = KeycloakOpenID(server_url=server_url, 
                                         client_id=client_id, 
                                         realm_name=realm_name) #verify=True?

        response = keycloak_openid.token(username, password)
        del password

        refresh_token = response['refresh_token']
        token_duration = response['expires_in']
        return keycloak_openid, refresh_token, token_duration
    except KeycloakError as e:
        print("Authentication failed: %s" % e) #L.error
        exit(1)



def token_periodic_call(keycloak_openid, refresh_token, token_duration, token_file):
    while True:
        refresh_token = _token_refresh(keycloak_openid, refresh_token, token_file)
        time.sleep(token_duration//2)

