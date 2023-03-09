import os
import requests
from fhirpy import AsyncFHIRClient

FHIR_URL = os.environ.get('EPIC_API_BASE_R4')
API_KEY = 'ad880601-b7e6-4d86-901d-b6fca96fc725'


def get_token():
    client_id = '44928fc1-17ae-4975-9c5e-ee2ba5ba1af1',
    client_secret = '22CBD4B98C2F04A082F08146FCE72F942B021903'
    url = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
    response = requests.post(url,
                             f'client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
    return response['access_token']


client = AsyncFHIRClient(
    FHIR_URL,
    authorization=f'Bearer {get_token()}',
    extra_headers={'x-api-key': API_KEY}
)
