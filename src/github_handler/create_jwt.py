import base64
import os
import time

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()

# We need to have Private Key of the GitHub App and the client ID of the GitHub App
# We then create a jwt token out of that using this code:

github_app_client_id = os.getenv("GITHUB_APP_CLIENT_ID")

github_app_private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")
github_app_private_key = github_app_private_key.replace(
    "-----BEGIN RSA PRIVATE KEY-----", ""
).replace("-----END RSA PRIVATE KEY-----", "")
key_bytes = base64.b64decode(github_app_private_key)

private_key = serialization.load_der_private_key(
    key_bytes, password=None, backend=default_backend()
)

# Code taken from https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app
current_time = int(time.time())
jwt_payload = {
    "iat": current_time,
    "exp": current_time + 120,  # This JWT token expires in 2 minutes
    "iss": github_app_client_id,
}

encoded_jwt = jwt.encode(payload=jwt_payload, key=private_key, algorithm="RS256")
