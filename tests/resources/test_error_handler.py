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

import pytest
from app.resources.error_handler import ECustomizedError
from app.resources.error_handler import customized_error_template

@pytest.mark.parametrize("test_input,expected", [(ECustomizedError.FILE_NOT_FOUND, "[File not found] %s."), \
    (ECustomizedError.INVALID_FILE_AMOUNT, "[Invalid file amount] must greater than 0"), \
        (ECustomizedError.JOB_NOT_FOUND, "[Invalid Job ID] Not Found"), \
            (ECustomizedError.FORGED_TOKEN, "[Invalid Token] System detected forged token, \
                    a report has been submitted."), \
                (ECustomizedError.TOKEN_EXPIRED, "[Invalid Token] Already expired."), \
                    (ECustomizedError.INVALID_TOKEN, "[Invalid Token] %s"), \
                        (ECustomizedError.INTERNAL, "[Internal] %s")])
def test_customized_error_template(test_input, expected):
    error = customized_error_template(test_input)
    assert error == expected


