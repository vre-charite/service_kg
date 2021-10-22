from pydantic import BaseModel, Field

class ImportResourcePost(BaseModel):
    '''
    the post request payload for import json resource to BBN
    '''
    dataset_code: list = None
    data: dict