import requests
from fastapi import APIRouter, BackgroundTasks, Header, File, UploadFile, Form, \
    Cookie
from typing import Optional
from fastapi_utils import cbv
import uuid

from ...models.resource_action import ImportResourcePost
from ...models.base_models import APIResponse, EAPIResponseCode

from ...commons.logger_services.logger_factory_service import SrvLoggerFactory

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
        self.__logger = SrvLoggerFactory('api_dataset_resource').get_logger()

    @router.post("/resources", tags=[_API_TAG], #, response_model=PreUploadResponse,
                 summary="API will create the new resources from user input.")
    @catch_internal(_API_NAMESPACE)
    async def import_resouces(self, request_payload: ImportResourcePost, \
        Authorization: Optional[str] = Header(None)):
        
        api_response = APIResponse()
        json_list = request_payload.data

        try:

            # here since we might have the token from portal OR cli
            # but cli has the secrete which BBN dont have so we have to enable 
            # cross client token exchange
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            payload = {
                "grant_type" : "urn:ietf:params:oauth:grant-type:token-exchange",
                "subject_token": Authorization.replace("Bearer ", ""),
                "subject_token_type":"urn:ietf:params:oauth:token-type:access_token",
                "requested_token_type": "urn:ietf:params:oauth:token-type:refresh_token",
                "client_id": "nexus-web",
            }
            result = requests.post(ConfigClass.KEYCLOAK_URL+"/auth/realms/vre/protocol/openid-connect/token", data=payload, headers=headers)
            at = result.json().get("access_token")

            # NOTE since the cli will need to know which file is processing
            # or being ignored, the payload will change to {"file_name": json}
            # and the return will also be "processing:{"file_name": json}
            processing, ignored = {}, {}
            for j_name, j_data in json_list.items(): 
                self.__logger.info(j_name, j_data)

                # block the empty json
                if len(j_data) == 0: continue

                # here we will validate the attribute VRE-1984
                # if @id not exist, the uuid will be used
                # if @type is not exist, the term `Not_Specified` will be used
                if j_data.get("@id") is None: j_data.update({"@id": str(uuid.uuid4())})
                if j_data.get("@type") is None: j_data.update({"@type": "Not_Specified"})
                if j_data.get("@context") is None: j_data.update({"@context": "https://context.org"})


                # but NOTE here i am not sure if the BBN has the batch action
                # the loop might cause the timeout or congesttion

                header = {"Authorization": "Bearer " + at}
                res = requests.post(ConfigClass.BBN_ENDPOINT+"/resources/%s/%s"\
                    %(ConfigClass.BBN_ORG, ConfigClass.BBN_PROJECT), json=j_data, headers=header)
                self.__logger.info(res.__dict__)
                if res.status_code >= 300:
                    j_data.update({"feedback":res.json().get("reason", "")})
                    ignored.update({j_name:j_data})
                else:
                    processing.update({j_name:res.json()})

            api_response.result = {
                "processing": processing,
                "ignored": ignored
            }
        except Exception as e:
            self.__logger.error(str(e))

        return api_response.json_response()