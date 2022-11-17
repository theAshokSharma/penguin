# Read all EPIC DSTU2 endpoints from 
# https://open.epic.com/Endpoints/DSTU2
# https://open.epic.com/Endpoints/R4


import json


def getEPICendpoint() -> None:
    with open('https://open.epic.com/Endpoints/R4', 'r') as f:
        data = json.load(f)

    return data


data = getEPICendpoint()
print(data)