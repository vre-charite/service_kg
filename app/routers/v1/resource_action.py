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

import httpx
from fastapi import APIRouter, Header
from typing import Optional
from fastapi_utils import cbv
import uuid

from ...models.resource_action import ImportResourcePost
from ...models.base_models import APIResponse, EAPIResponseCode

from logger import LoggerFactory

from ...resources.error_handler import catch_internal

from ...config import ConfigClass

router = APIRouter()

_API_TAG = 'V1 KG'
_API_NAMESPACE = "api_kg"

HEADERS = {"accept": "application/json", "Content-Type": "application/json"}


@cbv.cbv(router)
class APIImportData:
    '''
    API to operation on BBN resource
    '''

    def __init__(self):
        self.__logger = LoggerFactory('api_dataset_resource').get_logger()

    @router.post("/resources", tags=[_API_TAG],  # , response_model=PreUploadResponse,
                 summary="API will create the new resources from user input.")
    @catch_internal(_API_NAMESPACE)
    async def import_resouces(self, request_payload: ImportResourcePost, \
                              Authorization: Optional[str] = Header(None)):

        api_response = APIResponse()
        json_list = request_payload.data
        processing, ignored = {}, {}

        # here since we might have the token from portal OR cli
        # but cli has the secrete which BBN dont have so we have to enable 
        # cross client token exchange
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": Authorization.replace("Bearer ", ""),
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "requested_token_type": "urn:ietf:params:oauth:token-type:refresh_token",
            "client_id": "nexus-web",
        }
        async with httpx.AsyncClient() as client:
            result = await client.post(ConfigClass.KEYCLOAK_ENDPOINT,
                                       data=payload, headers=headers)

        self.__logger.info(f"result calling httpx, {result.json()}")
        at = result.json().get("access_token")
        if not at or result.status_code >= 300:
            self.__logger.error(result.json())
            api_response.error_msg = "fail to exchnage the token. " + str(result.json())
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()

        # NOTE since the cli will need to know which file is processing
        # or being ignored, the payload will change to {"file_name": json}
        # and the return will also be "processing:{"file_name": json}
        for j_name, j_data in json_list.items():
            try:
                self.__logger.info(j_name)
                self.__logger.info(j_data)

                # block the empty json
                if len(j_data) == 0: continue
                if type(j_data) != dict:
                    raise Exception("expect the data as dictionary but recieve %s" % (type(j_data)))

                # here we will validate the attribute '1984'
                # if @id not exist, the uuid will be used
                # if @type is not exist, the term `Not_Specified` will be used
                if j_data.get("@id") is None: j_data.update({"@id": str(uuid.uuid4())})
                if j_data.get("@type") is None: j_data.update({"@type": "Not_Specified"})
                if j_data.get("@context") is None: j_data.update({"@context": "https://context.org"})

                # but NOTE here i am not sure if the BBN has the batch action
                # the loop might cause the timeout or congesttion
                header = {"Authorization": "Bearer " + at}
                self.__logger.info(f"Calling payload: {j_data}")
                with httpx.Client() as client:
                    res = client.post(ConfigClass.BBN_ENDPOINT + "/resources/%s/%s" \
                                      % (ConfigClass.BBN_ORG, ConfigClass.BBN_PROJECT), json=j_data, headers=header)
                self.__logger.info(f"Response of creating the resource in kg: {res.json()}")
                if res.status_code >= 300:
                    j_data.update({"feedback": res.json().get("reason", "")})
                    ignored.update({j_name: j_data})
                else:
                    processing.update({j_name: res.json()})

            # if we catch ANY error, then this file will be ignored and
            # attach the error message as feedback
            except Exception as e:
                self.__logger.error(str(e))
                ignored.update({j_name: {"feedback": str(e)}})

        api_response.result = {
            "processing": processing,
            "ignored": ignored
        }

        return api_response.json_response()
