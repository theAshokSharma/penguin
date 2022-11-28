# http://build.fhir.org/ig/HL7/smart-app-launch/authorization-example-jwks-and-signatures.html
# To create a markdown of this notebook, 
# run: jupyter nbconvert --to markdown authorization-example-jwks-and-signatures.ipynb
# !pip3 install python-jose

import json
import jose.jwk
import jose.jwt
import jose.constants


def get_signing_key(filename):
    with open(filename) as private_key_file:
        signing_keyset = json.load(private_key_file)
        signing_key = [k for k in signing_keyset["keys"] if "sign" in k["key_ops"]][0]
        return signing_key


jwt_claims = {
  "iss": "https://bili-monitor.example.com",
  "sub": "https://bili-monitor.example.com",
  "aud": "https://authorize.smarthealthit.org/token",
  "exp": 1422568860,
  "jti": "random-non-reusable-jwt-id-123"
}


print("# Encoded JWT with RS384 Signature")
rsa_signing_jwk = get_signing_key("sample/RS384.private.json")
jose.jwt.encode(
    jwt_claims,
    rsa_signing_jwk,
    algorithm='RS384',
    headers={"kid": rsa_signing_jwk["kid"]})


print("# Encoded JWT with ES384 Signature")
ec_signing_jwk  = get_signing_key("sample/ES384.private.json")
jose.jwt.encode(
    jwt_claims,
    ec_signing_jwk,
    algorithm='ES384',
    headers={"kid": ec_signing_jwk["kid"]})
