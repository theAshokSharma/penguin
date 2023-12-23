# Read all EPIC DSTU2 endpoints from
# https://open.epic.com/Endpoints/DSTU2
# https://open.epic.com/Endpoints/R4

import json
import httpx


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
    # data = getEPICendpoint('https://open.epic.com/Endpoints/R4')
    # if data:
    #     endpnt = data["entry"]
    #     for i, itm in enumerate(endpnt):
    #         srcdata = itm["resource"]
    #         namedata = itm["resource"]["contained"][0]
    #         print(f'"{i+1}","{namedata["resourceType"]}","{srcdata["status"]}","{namedata["id"]}","{namedata["name"]}","{srcdata["address"]}"')

    data2 = getCERNERendpoint('https://raw.githubusercontent.com/cerner/ignite-endpoints/main/millennium_patient_r4_endpoints.json')
    if data2:
        endpnt = data2["entry"]
        for i, itm in enumerate(endpnt):
            srcdata = itm["resource"]
            namedata = itm["resource"]["contained"][0]
            print(f'"{i+1}","{namedata["resourceType"]}","{srcdata["status"]}","{namedata["id"]}","{namedata["name"]}","{srcdata["address"]}"')


if __name__ == '__main__':
    main()
