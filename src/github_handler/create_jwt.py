import os
import jwt
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# We need to have Private Key of the GitHub App and the client ID of the GitHub App

# We then create a jwt token out of that using this code:

github_app_private_key_path = "documentation-generator-brownmunda.2025-11-23.private-key.pem"
github_app_client_id = os.getenv("GITHUB_APP_CLIENT_ID")

pem_path = Path(github_app_private_key_path).resolve()

github_app_private_key = pem_path.read_bytes()

# Taken from https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app
current_time = int(time.time())
jwt_payload = {
    "iat": current_time,
    "exp": current_time + 120, # This JWT token expires in 2 minutes
    "iss": github_app_client_id
}

encoded_jwt = jwt.encode(payload=jwt_payload, key=github_app_private_key, algorithm="RS256")
