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
from pytest_httpx import HTTPXMock

@pytest.mark.asyncio
async def test_create_resource_should_be_proccessed(test_async_client, httpx_mock: HTTPXMock):
    headers = {"Authorization": "Fake Access Token"}
    httpx_mock.add_response(
        method='POST',
        url='http://fake_keycloak_url',
        json={
            "access_token":"fake access token",
            "refresh_token":"fake refresh",
            "token_type":"bearer"
        },
        status_code=200,
    )

    httpx_mock.add_response(
        method='POST',
        url='http://endpoint/kg/v1/resources/test_org/test_project',
        json={
            "resource_id": "test0111case1456"
        },
        status_code=200,
    )

    payload = {
            "dataset_code": [
                "test011"
            ],
            "data": {
                "test234.json": {
                    "resource_id": "test0111case1456",
                    "@type": "https://openminds.ebrains.eu/core/Dataset",
                    "description": "Resource description",
                    "digitalIdentifier": "https://localhost/digitalIdentifier/e433bfa2-22d4-11ec-a97f-0242ac110002",
                    "fullName": "Resrouce full name",
                    "shortName": "Rfn",
                    "@context": {
                        "@vocab": "https://vocab/"
                    }
                }
            }
        }
    res = await test_async_client.post('/v1/resources', json=payload, headers=headers)
    result = res.json()
    assert res.status_code == 200
    id = result["result"]["processing"]["test234.json"]["resource_id"]
    assert id == payload["data"]["test234.json"]["resource_id"]

@pytest.mark.asyncio
async def test_create_with_duplicate_resource_should_ignore(test_async_client, httpx_mock: HTTPXMock):
    headers = {"Authorization": "Fake Access Token"}
    httpx_mock.add_response(
        method='POST',
        url='http://fake_keycloak_url',
        json={
            "access_token":"fake access token",
            "refresh_token":"fake refresh",
            "token_type":"bearer"
        },
        status_code=200,
    )

    httpx_mock.add_response(
        method='POST',
        url='http://endpoint/kg/v1/resources/test_org/test_project',
        json={
            "resource_id": "test0111case1456"
        },
        status_code=300,
    )

    payload = {
            "dataset_code": [
                "test011"
            ],
            "data": {
                "test234.json": {
                    "resource_id": "test0111case1456",
                    "@type": "https://openminds.ebrains.eu/core/Dataset",
                    "description": "Resource description",
                    "digitalIdentifier": "https://localhost/digitalIdentifier/e433bfa2-22d4-11ec-a97f-0242ac110002",
                    "fullName": "Resrouce full name",
                    "shortName": "Rfn",
                    "@context": {
                        "@vocab": "https://vocab/"
                    }
                }
            }
        }
    res = await test_async_client.post('/v1/resources', json=payload, headers=headers)
    result = res.json()
    assert res.status_code == 200
    id = result["result"]["ignored"]["test234.json"]["resource_id"]
    assert id == payload["data"]["test234.json"]["resource_id"]

@pytest.mark.asyncio
async def test_create_resource_with_error_token(test_async_client, httpx_mock: HTTPXMock):
    headers = {"Authorization": "Wrong token"}
    httpx_mock.add_response(
            method='POST',
            url='http://fake_keycloak_url',
            json={
                "access_token":"error access token",
                "refresh_token":"error refresh",
                "token_type":"bearer"
            },
            status_code=300,
        )

    payload = {
            "dataset_code": [
                "test011"
            ],
            "data": {
                "test234.json": {
                    "resource_id": "test0111case1456",
                    "@type": "https://openminds.ebrains.eu/core/Dataset",
                    "description": "Resource description",
                    "digitalIdentifier": "https://localhost/digitalIdentifier/e433bfa2-22d4-11ec-a97f-0242ac110002",
                    "fullName": "Resrouce full name",
                    "shortName": "Rfn",
                    "@context": {
                        "@vocab": "https://vocab/"
                    }
                }
            }
        }
    res = await test_async_client.post('/v1/resources', json=payload, headers=headers)
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_create_resource_with_error_payload_should_ignore(test_async_client, httpx_mock: HTTPXMock):
    headers = {"Authorization": "Wrong token"}
    httpx_mock.add_response(
            method='POST',
            url='http://fake_keycloak_url',
            json={
                "access_token":"error access token",
                "refresh_token":"error refresh",
                "token_type":"bearer"
            },
            status_code=200,
        )

    payload = {
            "dataset_code": [
                "test011"
            ],
            "data": {
                "test234.json": "error_payload"
            }
        }
    
    res = await test_async_client.post('/v1/resources', json=payload, headers=headers)
    result = res.json()
    assert res.status_code == 200
    assert result["result"]["ignored"]["test234.json"] == {'feedback': "expect the data as dictionary but recieve <class 'str'>"}


