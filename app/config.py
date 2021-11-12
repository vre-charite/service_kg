import os
import requests
from requests.models import HTTPError

srv_namespace = "service_kg"
CONFIG_CENTER = "http://10.3.7.222:5062" \
    if os.environ.get('env', "test") == "test" \
    else "http://common.utility:5062"


def vault_factory() -> dict:
    url = CONFIG_CENTER + \
        "/v1/utility/config/{}".format(srv_namespace)
    config_center_respon = requests.get(url)
    if config_center_respon.status_code != 200:
        raise HTTPError(config_center_respon.text)
    return config_center_respon.json()['result']


class ConfigClass(object):
    vault = vault_factory()
    env = os.environ.get('env')
    disk_namespace = os.environ.get('namespace')
    version = "0.1.0"
    
    # blue brain nexus
    # TODO move it to vault
    BBN_ENDPOINT = "http://10.3.7.220/kg/v1" if os.environ.get('env', "test") == "test" else "http://nexus-delta.utility:80/kg/v1"
    BBN_ORG = "charite"
    BBN_PROJECT = "Lesion2TVB"

    # test keycloak endpoint NOTE update to dev later
    KEYCLOAK_URL = vault["KEYCLOAK_URL"] + '/vre'