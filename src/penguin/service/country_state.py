
# read country and state data
# https://github.com/dr5hn/countries-states-cities-database/blob/master/countries%2Bstates.json

import json
import httpx


def getCountryState(url: str = 'https://api.countrystatecity.in/v1/countries') -> None:
    '''
    get Country and state information for the world
    '''

    data = None
    certs = (
        "ssl/localhost.crt",
        "ssl/localhost.key")
    headers = {
        'X-CSCAPI-KEY': 'API_KEY'}
    response = httpx.get(url, cert=certs, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.read())

    return data


def main() -> None:
    data = getCountryState()
    if data:
        endpnt = data["entry"]
        # for i, itm in enumerate(endpnt):
        #     srcdata = itm["resource"]
        #     namedata = itm["resource"]["contained"][0]
        #     auth_ep, token_ep = getAuthTokenEndpoint(srcdata["address"])
        #     print(f'"{i+1}","{namedata["resourceType"]}","{srcdata["status"]}","{namedata["id"]}","{namedata["name"]}","{srcdata["address"]}","{auth_ep}","{token_ep}"')


if __name__ == '__main__':
    main()
