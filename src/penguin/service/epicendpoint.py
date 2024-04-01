# Read all EPIC DSTU2 endpoints from
# https://open.epic.com/Endpoints/DSTU2
# https://open.epic.com/Endpoints/R4

import json
import httpx


def getAuthTokenEndpoint(baseurl: str = 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4') -> None:
    baseurl = baseurl + ".well-known/smart-configuration"
    data = None
    auth_endpoint = None
    token_endpoint = None
    certs = (
        "ssl/localhost.crt",
        "ssl/localhost.key")
    try:
        response = httpx.get(baseurl, cert=certs)

        if response.status_code == 200:
            data = json.loads(response.read())

        auth_endpoint = data["authorization_endpoint"]
        token_endpoint = data["token_endpoint"]
    except:
        auth_endpoint = None
        token_endpoint = None

    return auth_endpoint, token_endpoint


def getEPICendpoint(url: str = 'https://open.epic.com/Endpoints/R4') -> None:
    '''
    get EPIC endpoint data from url dataset
    '''
    data = None
    certs = (
        "ssl/localhost.crt",
        "ssl/localhost.key")
    response = httpx.get(url, cert=certs)

    if response.status_code == 200:
        data = json.loads(response.read())

    return data


# https://raw.githubusercontent.com/cerner/ignite-endpoints/main/millennium_patient_r4_endpoints.json
def getCERNERendpoint(url: str = 'https://raw.githubusercontent.com/cerner/ignite-endpoints/main/millennium_patient_r4_endpoints.json') -> None:
    '''
    get CERNER endpoint data from url dataset
    '''
    data = None
    certs = (
        "ssl/localhost.crt",
        "ssl/localhost.key")
    response = httpx.get(url, cert=certs)

    if response.status_code == 200:
        data = json.loads(response.read())

    return data


def main() -> None:
    # auth_ep, token_ep = getAuthTokenEndpoint('https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/')
    data = getEPICendpoint('https://open.epic.com/Endpoints/R4')
    if data:
        endpnt = data["entry"]
        for i, itm in enumerate(endpnt):
            srcdata = itm["resource"]
            namedata = itm["resource"]["contained"][0]
            auth_ep, token_ep = getAuthTokenEndpoint(srcdata["address"])
            print(f'"{i+1}","{namedata["resourceType"]}","{srcdata["status"]}","{namedata["id"]}","{namedata["name"]}","{srcdata["address"]}","{auth_ep}","{token_ep}"')

    # data2 = getCERNERendpoint('https://raw.githubusercontent.com/cerner/ignite-endpoints/main/millennium_patient_r4_endpoints.json')
    # if data2:
    #     endpnt = data2["entry"]
    #     for i, itm in enumerate(endpnt):
    #         srcdata = itm["resource"]
    #         namedata = itm["resource"]["contained"][0]
    #         print(f'"{i+1}","{namedata["resourceType"]}","{srcdata["status"]}","{namedata["id"]}","{namedata["name"]}","{srcdata["address"]}"')


if __name__ == '__main__':
    main()
