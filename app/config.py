# Copyright 2022 Indoc Research
# 
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# 
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# 
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# 

import os
from pydantic import BaseSettings, Extra
from typing import Dict, Any
from functools import lru_cache
from common import VaultClient
from dotenv import load_dotenv

load_dotenv()
SRV_NAMESPACE = os.environ.get("APP_NAME", "service_kg")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")
VAULT_URL = os.getenv("VAULT_URL")
VAULT_CRT = os.getenv("VAULT_CRT")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        vc = VaultClient(VAULT_URL, VAULT_CRT, VAULT_TOKEN)
        vc_result = vc.get_from_vault(SRV_NAMESPACE)
        return vc_result


class Settings(BaseSettings):
    port: int = 5082
    host: str = "0.0.0.0"
    version: str = "0.1.0"
    env: str = ""
    disk_namespace: str = ""
    OPEN_TELEMETRY_ENABLED: str

    # blue brain nexus
    BBN_ENDPOINT: str = ""
    BBN_ORG: str = ""
    BBN_PROJECT: str = ""
    AUTH_SERVICE: str = ""

    # keycloak endpoint
    KEYCLOAK_ENDPOINT: str = ""

    def modify_values(self, settings):
        settings.AUTH_SERVICE = settings.AUTH_SERVICE + "/v1/"
        if settings.env != "test":
            settings.BBN_ENDPOINT = os.getenv("BBN_ENDPOINT")
    

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
    settings = Settings()
    settings.modify_values(settings)
    return settings


ConfigClass = get_settings()
