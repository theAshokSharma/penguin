from fhirclient import client
import fhirclient.models.patient as p

settings = {
    'app_id': 'my_web_app',
    'api_base': 'https://fhir-open-api-dstu2.smarthealthit.org'
}
smart = client.FHIRClient(settings=settings)


patient = p.Patient.read('hca-pat-1', smart.server)
patient.birthDate.isostring
# '1963-06-12'
smart.human_name(patient.name[0])
# 'Christy Ebert'