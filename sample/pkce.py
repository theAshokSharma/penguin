def get_pkce() -> Tuple[str, str, str]:
    """
    Calculates PKCE values

    Public Key for Code Exchange is an extension to OAuth2 to mitigate the risk of interception attacks. There is not
    yet support in MSAL Python (see https://github.com/AzureAD/microsoft-authentication-library-for-python/issues/255).

    See https://www.stefaanlippens.net/oauth-code-flow-pkce.html for reference to this code snippet
    See https://marvelapp.com/developers/documentation/authentication/pkce for additional information

    As suggested in https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#request-an-authorization-code,
    we use S256 as code_challenge_method.

    Returns:
        A list containing the code verifier, the code challenge and the code challenge method (in that order)

    """

    code_verifier = urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)

    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')

    return code_verifier, code_challenge, "S256"


def get_auth_response(auth_url: str, hint_redirect_uri) -> str:
    authorization_response = None

    # open browser to that url
    if not webbrowser.open(url=auth_url, new=1, autoraise=True):
        authorization_response = input("""Unable to open default web browser. 
            Go to a web browser and enter the following URL: {0}. 
            Come back here and enter the full redirect URL. This should look similar to {1}.
            Consent might have to be granted on first usage.""".format(
            auth_url, hint_redirect_uri
        ))
    else:
        authorization_response = input("""The default web browser was opened. 
            Please grant consent to the application if requested. 
            Come back here and enter the full redirect URL. This should look similar to {}""".format(
            hint_redirect_uri
        ))

    return authorization_response


def _get_auth_code(response: str, state: Optional[str]=None) -> str:
    parsed = urlparse(response)
    params = parse_qs(parsed.query)
    if state:
        # if state is provided then check against state returned via redirect URI
        if state != params['state'][0]:
            raise Exception("Find some more suitable exception next time")

    return params['code'][0]


def get_ident_code_grant():
    """
    Sets up authorization and authentication in the context of a public client application using auth code grant

    Returns:

    """
    response_type: str = "code"
    response_mode: str = "query"
    # redirect_uri needs to be provided and must match the configured one in App registration
    redirect_uri: str = "https://login.microsoftonline.com/common/oauth2/nativeclient"
    state: str = str(uuid.uuid4())
    code_verifier, code_challenge, code_challenge_method = get_pkce()

    # Assemble final URL with PKCE parameters and response mode (as recommended parameters)
    auth_request_url = requests.Request(method='GET',
                                        url="https://login.microsoftonline.com/{}/oauth2/v2.0/authorize".format(TENANT_ID),
                                        params={"client_id": CLIENT_ID,
                                                "response_type": response_type,
                                                "redirect_uri": redirect_uri,
                                                "scope": ["https://{}.blob.core.windows.net/user_impersonation".format(STORAGE_NAME)],
                                                "response_mode": response_mode,
                                                "state": state,
                                                "code_challenge": code_challenge,
                                                "code_challenge_method": code_challenge_method}
                                        ).prepare().url

    # Retrieve authorization response from auth end point
    authorization_response = get_auth_response(auth_request_url, redirect_uri)

    # Parse authentication code and verify state from redirect URI
    # Based on https://stackoverflow.com/questions/5074803/retrieving-parameters-from-a-url)
    code = _get_auth_code(authorization_response, state)

    token = AuthorizationCodeCredential(tenant_id=TENANT_ID,
                                        client_id=CLIENT_ID,
                                        authorization_code=code,
                                        redirect_uri=redirect_uri)
    return token


def download_blob(token):
    container_client = ContainerClient(account_url="https://{}.blob.core.windows.net".format(STORAGE_NAME),
                                       container_name="test",
                                       credential=token)
    blob_client = container_client.get_blob_client("test.png")

    with open("./BlockDestination.txt", "wb") as my_blob:
        blob_data = blob_client.download_blob()
        blob_data.readinto(my_blob)


if __name__ == "__main__":
    token = get_ident_code_grant()
    download_blob(token)
