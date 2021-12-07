import os
import requests
from requests.models import HTTPError
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache

SRV_NAMESPACE = os.environ.get("APP_NAME", "service_kg")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")
CONFIG_CENTER_BASE_URL = os.environ.get("CONFIG_CENTER_BASE_URL", "NOT_SET")

def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        return vault_factory(CONFIG_CENTER_BASE_URL)

def vault_factory(config_center) -> dict:
    url = f"{config_center}/v1/utility/config/{SRV_NAMESPACE}"
    config_center_respon = requests.get(url)
    if config_center_respon.status_code != 200:
        raise HTTPError(config_center_respon.text)
    return config_center_respon.json()['result']


class Settings(BaseSettings):
    port: int = 5082
    host: str = "127.0.0.1"
    env: str = "test"
    namespace: str = ""
    
    # blue brain nexus
    # TODO move it to vault
    BBN_ENDPOINT_TEST: str = "http://10.3.7.220/kg/v1" 
    BBN_ENDPOINT: str = "http://nexus-delta.utility:80/kg/v1"
    BBN_ORG: str = "charite"
    BBN_PROJECT: str  = "VRE_Datasets"

    # test keycloak endpoint NOTE update to dev later
    KEYCLOAK_URL: str 
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                load_vault_settings,
                env_settings,
                init_settings,
                file_secret_settings,
            )
    

@lru_cache(1)
def get_settings():
    settings =  Settings()
    return settings

class ConfigClass(object):
    settings = get_settings()

    version = "0.1.0"
    env = settings.env
    disk_namespace = settings.namespace
    
    # blue brain nexus
    # TODO move it to vault
    BBN_ENDPOINT = settings.BBN_ENDPOINT_TEST if env == "test" else settings.BBN_ENDPOINT
    BBN_ORG = settings.BBN_ORG
    BBN_PROJECT = settings.BBN_PROJECT

    # test keycloak endpoint NOTE update to dev later
    KEYCLOAK_URL = settings.KEYCLOAK_URL + '/vre'