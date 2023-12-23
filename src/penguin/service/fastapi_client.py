import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import uvicorn

# from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
# from authlib.integrations.starlette_client import OAuth, OAuthError

from fhirclient import client
from fhirclient.models.allergyintolerance import AllergyIntolerance

from penguin.model.patientinfo import PatientInfo
from penguin.model.patientcondition import PatientCondition
from penguin.model.patientimmunization import PatientImmunization
from penguin.model.patientobservations import PatientObservation
from penguin.model.patientdiagnosticreport import PatientDiagnosticReport
from penguin.model.patientprescription import PatientPrescription
from penguin.model.patientallergies import PatientAllergies

REQ: Request = None

# app setup

# The settings dictionary supports:

#     - `app_id`*: Your app/client-id, e.g. 'my_web_app'
#     - `app_secret`*: Your app/client-secret
#     - `api_base`*: The FHIR service to connect to, e.g. 'https://fhir-api-dstu2.smarthealthit.org'
#     - `redirect_uri`: The callback/redirect URL for your app, e.g. 'http://localhost:8000/fhir-app/'
#        when testing locally
#     - `patient_id`: The patient id against which to operate, if already known
#     - `scope`: Space-separated list of scopes to request, if other than default
#     - `launch_token`: The launch token
#     - `jwt_token`:

smart_scope = 'patient/Patient.read'
smart_scope += ' patient/Observation.read'
smart_scope += ' patient/Immunization.read'
smart_scope += ' patient/Medication.read'
smart_scope += ' patient/MedicationRequest.read'
smart_scope += ' patient/AllergyIntolerance.read'
smart_scope += ' patient/DiagnosticReport.read'
smart_scope += ' patient/Procedure.read'
smart_scope += ' patient/Condition.read'
smart_scope += ' launch/patient fhirUser online_access openid profile'

# smart_defaults = {
#     'app_id': os.environ.get("ATHENA_CLIENT_ID"),
#     'api_base': os.environ.get('ATHENA_API_BASE'),
#     'redirect_uri': os.environ.get('APP_REDIRECT_URL'),
#     'scope': smart_scope,
#     'code_challenge': 'test',
#     'launch_token': ''
# }

# smart_defaults = {
#     'app_id': os.environ.get("EPIC_CLIENT_ID"),
#     'api_base': os.environ.get('EPIC_API_BASE'),
#     'redirect_uri': os.environ.get('APP_REDIRECT_URL'),
#     'scope': smart_scope,
#     'launch_token': ''
# }

smart_defaults = {
    'app_id': os.environ.get("CERNER_CLIENT_ID"),
    'api_base': os.environ.get('CERNER_API_BASE'),
    'redirect_uri': os.environ.get('APP_REDIRECT_URL'),
    'scope': smart_scope,
    'launch_token': ''
}


def _save_state(state):
    REQ.session['state'] = state


def _get_smart():
    state = REQ.session.get('state')

    if state:
        if state["app_id"] != smart_defaults["app_id"]:
            _reset()
            state = None

    if state:
        return client.FHIRClient(state=state,
                                 save_func=_save_state)
    else:
        return client.FHIRClient(settings=smart_defaults,
                                 save_func=_save_state)


def _logout():
    if 'state' in REQ.session:
        smart = _get_smart()
        smart.reset_patient()


def _reset():
    if 'state' in REQ.session:
        del REQ.session['state']


def _get_allergies(smart):
    try:
        resources = AllergyIntolerance.where(struct={'patient': smart.patient_id}).\
            perform_resources(smart.server)

        resources_ = [src for src in resources if src.resource_type != 'OperationOutcome']
    except Exception as e:
        resources_ = None

    return resources_


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
        return HTMLResponse("""<h1>Authorization Error:</h1><p>{0}</p><p><a href="/">Start over</a></p>""".
        format(e))

    body = """<p><a href="/logout">Change patient</a></p>"""
    body += "<h1>Hello</h1>"
    if smart.ready and smart.patient is not None:

        pat = PatientInfo.fromFHIRPatient(smart.patient)

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

        pres = PatientPrescription.get_patient_presecriptions(smart)
        if pres is not None:
            body += "<p>{0} prescriptions: <ul><li>{1}</li></ul></p>".format(
                "His" if 'male' == smart.patient.gender else "Her", '</li><li>'.
                join([rec.toString() for rec in pres]))
#                join([_get_med_name(p, smart) for p in pres]))
        else:
            body += "<p>(There are no prescriptions for {0})</p>".format(
                "him" if 'male' == smart.patient.gender else "her")

        cond_rec = PatientCondition.get_patient_conditions(smart)
        if cond_rec is not None:
            body += "<p>Conditions: <ul><li>{0}</li></ul></p>".format('</li><li>'.
            join([rec.toString() for rec in cond_rec]))
        else:
            body += "<p>Conditions: <ul><li><strong>Not Found</strong></li></ul></p>"

        diagnostic_recs = PatientDiagnosticReport.get_patient_diagnostic_report(smart)
        if diagnostic_recs is not None:
            body += "<p>Diagnostic: <ul><li>{0}</li></ul></p>".format('</li><li>'.
            join([rec.toString() for rec in diagnostic_recs]))
        else:
            body += "<p>Diagnostic: <ul><li><strong>Not Found</strong></li></ul></p>"

        obs_vs = PatientObservation.get_patient_vital_signs(smart)
        if obs_vs is not None:
            body += "<p>Vitals: <ul><li>{0}</li></ul></p>".format('</li><li>'.
            join([rec.toString() for rec in obs_vs]))
        else:
            body += "<p>Vitals: <ul><li><strong>Not Found</strong></li></ul></p>"

        alrgy_rec = PatientAllergies.get_patientAllergies(smart)
        if alrgy_rec is not None:
            body += "<p>Allergies: <ul><li>{0}</li></ul></p>".format('</li><li>'.
            join([rec.toString() for rec in alrgy_rec]))
        else:
            body += "<p>Allergies: <ul><li><strong>Not Found</strong></li></ul></p>"

        immz_rec = PatientImmunization.get_patientImmunization(smart)
        if immz_rec is not None:
            body += "<p>Immunizations: <ul><li>{0}</li></ul></p>".format('</li><li>'.
            join([rec.toString() for rec in immz_rec]))
        else:
            body += "<p>Immunizations: <ul><li><strong>Not Found</strong></li></ul></p>"

        lab_reslts = PatientObservation.get_patient_lab_results(smart)
        if lab_reslts is not None:
            body += "<p>Test Results: <ul><li>{0}</li></ul></p>".format('</li><li>'.
            join([rec.toString() for rec in lab_reslts]))
        else:
            body += "<p>Test Results: <ul><li><strong>Not Found</strong></li></ul></p>"

        sh_reslts = PatientObservation.get_patient_social_history(smart)
        if sh_reslts is not None:
            body += "<p>Social History: <ul><li>{0}</li></ul></p>".format('</li><li>'.
            join([rec.toString() for rec in sh_reslts]))
        else:
            body += "<p>Social History: <ul><li><strong>Not Found</strong></li></ul></p>"

        body += "<p>Procedures: <ul><li><strong>Not Found</strong></li></ul></p>"

    return HTMLResponse(body)


@app.get("/logout", response_class=HTMLResponse)
def login_get():
    _logout()
    _reset()
    response = RedirectResponse(url="/")
    return response


@app.get('/reset', response_class=HTMLResponse)
def reset():
    _logout() 
    _reset()
    response = RedirectResponse(url="/")
    return response


if __name__ == '__main__':
    uvicorn.run("fastapi_client:app",
                host='localhost',
                port=5465,
                log_level="info",
                reload=True,
                ssl_keyfile="ssl/localhost.key",
                ssl_certfile="ssl/localhost.crt")
    print("running")
