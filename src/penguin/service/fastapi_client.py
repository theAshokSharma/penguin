import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import uvicorn

# from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse
# from authlib.integrations.starlette_client import OAuth, OAuthError

from fhirclient import client
from fhirclient.models.medication import Medication
from fhirclient.models.medicationrequest import MedicationRequest
from fhirclient.models.contactpoint import ContactPoint

REQ: Request = None

# app setup
smart_defaults = {
    'app_id': os.environ.get("EPIC_CLIENT_ID"),
    'api_base': os.environ.get('EPIC_API_BASE_R4'),
    'redirect_uri': os.environ.get('EPIC_REDIRECT_URL'),
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
    pres = [be.resource for be in bundle.entry] if bundle is not None and bundle.entry is not None else None
    if pres is not None and len(pres) > 0:
        return pres
    return None


def _get_medication_by_ref(ref, smart):
    med_id = ref.split("/")[1]
    return Medication.read(med_id, smart.server).code


def _med_name(med):
    if med.coding:
        name = next((coding.display for coding in med.coding
                     if coding.system == 'http://www.nlm.nih.gov/research/umls/rxnorm'), None)
        if name:
            return name
    if med.text and med.text:
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
        return "unmanaged resource type: {0}".format(prescription.resource_type)


def _get_contact(contactinfo: ContactPoint):
    if contactinfo is not None:
        if contactinfo.system == 'phone':
            return "{0} - {1}({2})".format(contactinfo.system if contactinfo.system is not None else "unknown",
                                           contactinfo.value if contactinfo.value is not None else "unknown",
                                           contactinfo.use if contactinfo.use is not None else "unknown")
        else:
            return "{0} - {1}".format(contactinfo.system if contactinfo.system is not None else "unknown",
                                contactinfo.value if contactinfo.value is not None else "unknown")
    return "unknown - unknown"


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
            body += "<p>{0} prescriptions: <ul><li>{1}</li></ul></p>".format("His" if 'male' == smart.patient.gender else "Her", '</li><li>'.join([_get_med_name(p, smart) for p in pres]))
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
        name = smart.human_name(smart.patient.name[0]
                if smart.patient.name and len(smart.patient.name) > 0 else 'Unknown')
        dob = smart.patient.birthDate.isostring if smart.patient.birthDate is not None else None
        patientID = smart.patient_id

        # generate simple body text
        body += "<p>You are authorized and ready to make API requests for <em>{0}</em>.</p>".format(name)
        body += "<p>Birth Date: {0}</p>".format(dob)
        body += "<p>ID: {0}</p>".format(patientID)

        # get all contact number
        body += "<p>Contact Information(s): <ul><li>{0}</li></ul></p>".format('</li><li>'.join([_get_contact(cntc) for cntc in smart.patient.telecom]))

        pres = _get_prescriptions(smart)
        if pres is not None:
            body += "<p>{0} prescriptions: <ul><li>{1}</li></ul></p>".format("His" if 'male' == smart.patient.gender else "Her", '</li><li>'.join([_get_med_name(p, smart) for p in pres]))
        else:
            body += "<p>(There are no prescriptions for {0})</p>".format("him" if 'male' == smart.patient.gender else "her")
        body += """<p><a href="/logout">Change patient</a></p>"""

    return HTMLResponse(body)


if __name__ == '__main__':
    uvicorn.run("fastapi_client:app",
                host='127.0.0.1',
                port=9050,
                log_level="info",
                reload=True)
#                # ssl_keyfile="../ssl/localhost.key",
#                # ssl_certfile="../ssl/localhost.crt")
    print("running")
