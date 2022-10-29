
import json
from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.immunization as im

settings = {
    'app_id': 'my_web_app',
    'api_base': 'http://hapi.fhir.org/baseR4',
    'content': 'application/fhir+json;charset=utf-8',
}


def print_resource(resource, indent=None, length=100):
    s = json.dumps(resource.as_json(), indent=indent)
    print(s[: length - 4] + ' ...' if len(s) > length else s)


smart = client.FHIRClient(settings=settings)


patient = p.Patient.read("53373", smart.server)
print(patient.birthDate.isostring)
print(smart.human_name(patient.name[0]))

search = im.Immunization.where(struct={'patient': '53373'})
immunizations = search.perform_resources(smart.server)
for imm in immunizations:
    print_resource(imm)
