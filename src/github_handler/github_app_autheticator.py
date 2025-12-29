# Use these github api endpoints for getting the installation id of a github app
# GET /users/{username}/installation, GET /repos/{owner}/{repo}/installation, GET /orgs/{org}/installation

# from github.GithubApp import GithubApp.

import warnings

warnings.filterwarnings("ignore")

import requests

from constants import GITHUB_API_URL
from github_handler.create_jwt import encoded_jwt

# Using the users endpoint
GITHUB_APP_INSTALLATION_ID_URL = GITHUB_API_URL + "/users/BrownMunda1/installation"

headers = {
    "Authorization": "Bearer " + encoded_jwt,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

response = requests.get(
    url=GITHUB_APP_INSTALLATION_ID_URL, headers=headers, timeout=10, verify=False
)

# print("GET INSTALLATION ID:", response.json())

github_app_installation_id = response.json().get("app_id", None)
access_token_url = response.json().get("access_tokens_url", None)

if not access_token_url:
    access_token_url = (
        GITHUB_API_URL
        + f"/app/installations/{github_app_installation_id}/access_tokens"
    )

access_token_response = requests.post(
    url=access_token_url, headers=headers, timeout=10, verify=False
)

# print("GET ACCESS TOKEN:", access_token_response.json())

github_access_token = access_token_response.json().get("token", None)
