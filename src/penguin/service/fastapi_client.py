import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import uvicorn

# from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
# from authlib.integrations.starlette_client import OAuth, OAuthError

from fhirclient import client
from fhirclient.models.medication import Medication
from fhirclient.models.medicationrequest import MedicationRequest
from fhirclient.models.immunization import Immunization
from fhirclient.models.observation import Observation
from fhirclient.models.observation import ObservationComponent
from fhirclient.models.allergyintolerance import AllergyIntolerance
from fhirclient.models.condition import Condition

from penguin.model.patientinfo import PatientInfo
from penguin.model.patientcondition import PatientCondition

REQ: Request = None

# app setup
smart_defaults = {
    'app_id': os.environ.get("EPIC_CLIENT_ID"),
    'api_base': os.environ.get('EPIC_API_BASE_R4'),
    'redirect_uri': os.environ.get('APP_REDIRECT_URL'),
    'launch_token': '',
    'jwt_token': ''
}


def _save_state(state):
    REQ.session['state'] = state


def _get_smart():
    state = REQ.session.get('state')

    if state:
        return client.FHIRClient(state=state, save_func=_save_state)
    else:
        return client.FHIRClient(settings=smart_defaults, save_func=_save_state)


def _logout():
    if 'state' in REQ.session:
        smart = _get_smart()
        smart.reset_patient()


def _reset():
    if 'state' in REQ.session:
        del REQ.session['state']


def _get_prescriptions(smart):
    bundle = MedicationRequest.where({'patient': smart.patient_id}).perform(smart.server)
    pres = [be.resource for be in bundle.entry] if bundle is not None and \
        bundle.entry is not None else None

    if pres is not None and len(pres) > 0:
        return pres
    return None


def _get_immunization(smart):
    bundle = Immunization.where({'patient': smart.patient_id}).perform(smart.server)
    imnzs = [be.resource for be in bundle.entry] if bundle is not None and \
        bundle.entry is not None else None

    imnz = [im for im in imnzs if im.resource_type != 'OperationOutcome']
    return imnz


def _get_immunization_details(imnz_J):
    return "{0} {1} {2} {3} Manufacturer: {4} Lot# {5} Status: {6}".format(
        imnz_J['occurrenceDateTime'],
        imnz_J['vaccineCode']['text'],
        imnz_J['doseQuantity']['value'],
        imnz_J['doseQuantity']['unit'],
        imnz_J['manufacturer']['display'],
        imnz_J['lotNumber'],
        imnz_J['status'])


def _get_observation_vitalsigns(smart):
    resources = Observation.where(struct={'patient': smart.patient_id, 'category': 'vital-signs'}).\
        perform_resources(smart.server)

    resources_ = [src for src in resources if src.resource_type != 'OperationOutcome']
    return resources_


def _get_allergies(smart):
    resources = AllergyIntolerance.where(struct={'patient': smart.patient_id}).\
        perform_resources(smart.server)

    resources_ = [src for src in resources if src.resource_type != 'OperationOutcome']
    return resources_


def _get_observation_component_data(obsComponent: ObservationComponent):
    details = "  ".join([c.code.text + " " +
        str(c.valueQuantity.value) + " " +
        c.valueQuantity.unit for c in obsComponent])
    return details


def _get_observation_details_vitalsigns(vs: Observation):
    vs_text = vs.code.text
    effdate = vs.effectiveDateTime.isostring
    issdate = vs.issued.isostring

    if vs.component is not None:
        obsdata = _get_observation_component_data(vs.component)
    elif vs.valueQuantity is not None:
        obsdata = str(vs.valueQuantity.value) + " " + vs.valueQuantity.unit
    else:
        obsdata = ""
    return "{0} {1} {2} {3}".format(effdate, issdate, vs_text, obsdata)


def _get_medication_by_ref(ref, smart):
    med_id = ref.split("/")[1]
    return Medication.read(med_id, smart.server).code


def _med_name(med):
    if med.coding:
        name = next((coding.display for coding in med.coding
                     if coding.system == 'http://www.nlm.nih.gov/research/umls/rxnorm'), None)
        if name:
            return name
    if med.text:
        return med.text
    return "Unnamed Medication(TM)"


def _get_med_name(prescription, client=None):
    if prescription.resource_type == 'MedicationRequest':
        if prescription.medicationCodeableConcept is not None:
            med = prescription.medicationCodeableConcept
            return _med_name(med)
        elif prescription.medicationReference is not None and client is not None:
            med = _get_medication_by_ref(prescription.medicationReference.reference, client)
            return _med_name(med)
        else:
            return 'Error: medication not found'
    else:
        return ""  # "unmanaged resource type: {0}".format(prescription.resource_type)


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="KeepThisSecret")


@app.get("/")
def root(request: Request):
    """ The app's main page.
    """
    global REQ
    REQ = request
    smart = _get_smart()
    body = "<h1>Hello</h1>"

    # "ready" may be true but the access token may have expired, making smart.patient = None
    if smart.ready and smart.patient is not None:
        name = smart.human_name(smart.patient.name[0]
                if smart.patient.name and len(smart.patient.name) > 0 else 'Unknown')
        dob = smart.patient.birthDate if smart.patient.birthDate is not None else None
        patientID = smart.patient_id

        # generate simple body text
        body += "<p>You are authorized and ready to make API requests for <em>{0}</em>.</p>".format(name)
        body += "<p><strong>Birth Date: </strong>{0}</p>".format(dob)
        body += "<p><strong>Birth Date: </strong>{0}</p>".format(patientID)

        pres = _get_prescriptions(smart)
        if pres is not None:
            body += "<p>{0} prescriptions: <ul><li>{1}</li></ul></p>".format(
                "His" if 'male' == smart.patient.gender else "Her", '</li><li>'.join([_get_med_name(p, smart) for p in pres]))
        else:
            body += "<p>(There are no prescriptions for {0})</p>".\
                format("him" if 'male' == smart.patient.gender else "her")
        body += """<p><a href="/logout">Change patient</a></p>"""
    else:
        auth_url = smart.authorize_url
        if auth_url is not None:
            body += """<p>Please <a href="{0}">authorize</a>.</p>""".format(auth_url)
        else:
            body += """<p>Running against a no-auth server, nothing to demo here. """
        body += """<p><a href="/reset" style="font-size:small;">Reset</a></p>"""
    return HTMLResponse(body)


@app.get('/fhir-app/')
def callback(request: Request, response_class=RedirectResponse):
    """ OAuth2 callback interception.
    """
    smart = _get_smart()
    try:
        smart.handle_callback(request.url._url)
    except Exception as e:
        return HTMLResponse("""<h1>Authorization Error</h1><p>{0}</p><p><a href="/">Start over</a></p>""".format(e))

    body = "<h1>Hello</h1>"
    if smart.ready and smart.patient is not None:

        pat = PatientInfo.fromFHIRPatient(smart.patient)

        alrgy_rec = _get_allergies(smart)
        cond_rec = PatientCondition.get_conditions(smart)

        # generate simple body text
        body += "<p>Patient <em>{0}</em>.</p>".format(pat.full_name())
        body += "<p>ID: <strong>{0}</strong></p>".format(pat.patientID)
        body += "<p>Birth Date: <strong>{0}</strong></p>".format(pat.birth_date)
        body += "<p>Marital Status: <strong>{0}</strong></p>".format(pat.marital_status)
        body += "<p>Language: <strong>{0}</strong></p>".format(pat.preferred_lang)
        body += "<p>General Practioner: <strong>{0}</strong></p>".format(pat.practitioner)

        # get all contact number
        body += "<p>Mobile Phone: <strong>{0}</strong></p>".format(pat.phone_mobile)
        body += "<p>Home Phone: <strong>{0}</strong></p>".format(pat.phone_home)
        body += "<p>Work Phone: <strong>{0}</strong></p>".format(pat.phone_work)

        # get all home address on the record
        body += "<p>Address:</p>"
        body += "<strong>{0}</strong><br>".format(pat.home_address["line1"])
        body += "<strong>{0}</strong><br>".format(pat.home_address["line2"])
        body += "<strong>{0}, {1} {2}</strong><br>".format(pat.home_address["city"],
            pat.home_address['state'], pat.home_address['zip_code'])
        body += "<strong>{0}</strong><br>".format(pat.home_address["country"])

        pres = _get_prescriptions(smart)
        if pres is not None:
            body += "<p>{0} prescriptions: <ul><li>{1}</li></ul></p>".format(
                "His" if 'male' == smart.patient.gender else "Her", '</li><li>'.
                join([_get_med_name(p, smart) for p in pres]))
        else:
            body += "<p>(There are no prescriptions for {0})</p>".format(
                "him" if 'male' == smart.patient.gender else "her")

        obs_rec = _get_observation_vitalsigns(smart)
        if obs_rec is not None:
            body += "<p>Vitals: <ul><li>{0}</li></ul></p>".format('</li><li>'.
            join([_get_observation_details_vitalsigns(rec) for rec in obs_rec]))
        else:
            body += "<p>Vitals: <ul><li><strong>Not Found</strong></li></ul></p>"

        body += "<p>Allergies: <ul><li><strong>Not Found</strong></li></ul></p>"

        immz_rec = _get_immunization(smart)
        if immz_rec is not None:
            body += "<p>Immunizations: <ul><li>{0}</li></ul></p>".format('</li><li>'.
            join([_get_immunization_details(rec.as_json()) for rec in immz_rec]))
        else:
            body += "<p>Immunizations: <ul><li><strong>Not Found</strong></li></ul></p>"

        body += "<p>Test Results: <ul><li><strong>Not Found</strong></li></ul></p>"
        body += "<p>Lab Results: <ul><li><strong>Not Found</strong></li></ul></p>"
        body += "<p>Conditions: <ul><li><strong>Not Found</strong></li></ul></p>"
        body += "<p>Procedures: <ul><li><strong>Not Found</strong></li></ul></p>"
        body += "<p>FAmily History: <ul><li><strong>Not Found</strong></li></ul></p>"

        body += """<p><a href="/logout">Change patient</a></p>"""
    return HTMLResponse(body)


@app.get("/logout", response_class=HTMLResponse)
def login_get():
    _logout()
    response = RedirectResponse(url="/")
    return response


@app.get('/reset', response_class=HTMLResponse)
def reset():
    _reset()
    response = RedirectResponse(url="/")
    return response


if __name__ == '__main__':
    uvicorn.run("fastapi_client:app",
                host='127.0.0.1',
                port=5465,
                log_level="info",
                reload=True)
#                # ssl_keyfile="../ssl/localhost.key",
#                # ssl_certfile="../ssl/localhost.crt")
    print("running")
