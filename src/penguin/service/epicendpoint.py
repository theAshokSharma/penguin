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


def main() -> None:
    data = getEPICendpoint('https://open.epic.com/Endpoints/DSTU2')
    if data:
        EPICep = data["entry"]
        for i, itm in enumerate(EPICep):
            srcdata = itm["resource"]
            print(f'{srcdata["resourceType"]}, {srcdata["status"]}, {srcdata["name"]}, {srcdata["address"]}')


if __name__ == '__main__':
    main()
