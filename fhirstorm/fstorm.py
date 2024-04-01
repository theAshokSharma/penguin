import os
from fhirstorm import Connection, auth

# https://github.com/Arborian/fhirstorm/blob/master/example/auto-register/app.py

# Replace with the service root of your SMART on FHIR endpoint
SERVICE_ROOT = os.environ.get('EPIC_API_BASE')
CLIENT_ID = os.environ.get("EPIC_CLIENT_ID")
REDIRECT_URI = os.environ.get('APP_REDIRECT_URL')
CLIENT_SECRET = 'there is no such thing called client secret'
INTERNAL_SECRET = 'itsaseekrit'  # please do better than this

# You need this if you used a `http://localhost...` redirect url
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

conn = Connection(SERVICE_ROOT)

# Get the particular REST endpoint (there's usually just the one)
service = conn.metadata.rest[0]

# Get your authorization url
authorization_url, state = auth.authorization_url(
    service,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope='profile openid offline_access launch/patient patient/*.*',
    state=auth.jwt_state(INTERNAL_SECRET),
    aud=SERVICE_ROOT)

# Assuming you've stored the actual redirect URL received into authorization response...

tok = auth.fetch_token(
    service, CLIENT_ID, REDIRECT_URI,
    authorization_response,
    client_secret=CLIENT_SECRET,        # if you have one, otherwise leave it off
    state_validator=auth.jwt_state_validator(INTERNAL_SECRET))

# Or if you saved the state:
tok = auth.fetch_token(
    service, CLIENT_ID, REDIRECT_URI,
    authorization_response,
    client_secret=CLIENT_SECRET,        # if you have one, otherwise leave it off
    state=STATE_VALUE_YOU_SAVED)
