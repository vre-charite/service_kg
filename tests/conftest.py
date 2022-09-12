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

from fastapi.testclient import TestClient
from async_asgi_testclient import TestClient as TestAsyncClient

from app.config import ConfigClass
from run import app

@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def test_async_client():
    return TestAsyncClient(app)


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr(ConfigClass, 'BBN_PROJECT', 'test_project')
    monkeypatch.setattr(ConfigClass, 'BBN_ORG', 'test_org')
    monkeypatch.setattr(ConfigClass, 'KEYCLOAK_ENDPOINT', 'http://fake_keycloak_url')
    monkeypatch.setattr(ConfigClass, 'BBN_ENDPOINT', 'http://endpoint/kg/v1')
    monkeypatch.setattr(ConfigClass, 'env', 'test')
