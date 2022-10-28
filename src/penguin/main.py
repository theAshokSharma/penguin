
import json
from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.procedure as pr

settings = {
    'app_id': 'my_web_app',
    'api_base': 'http://hapi.fhir.org/baseR4',
    'content': 'application/fhir+json;charset=utf-8',
}


def print_resource(resource, indent=None, length=100):
    s = json.dumps(resource.as_json(), indent=indent)
    print(s[: length - 4] + ' ...' if len(s) > length else s)


smart = client.FHIRClient(settings=settings)


patient = p.Patient.read("2687129", smart.server)
print(patient.birthDate.isostring)
print(smart.human_name(patient.name[0]))

search = pr.Procedure.where(struct={'subject': '2687129', 'status': 'completed'})
procedures = search.perform_resources(smart.server)
for procedure in procedures:
    print_resource(procedure)

search = search.include('subject')
procedures = search.perform_resources(smart.server)
for resource in procedures:
    print(resource.__class__.__name__)
    print_resource(resource)
