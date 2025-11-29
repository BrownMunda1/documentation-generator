import shutil
import base64
from pathlib import Path

import requests
from pydantic import HttpUrl

from github_handler.github_app_autheticator import github_access_token
from constants import GITHUB_API_URL

def clone(repo_url: HttpUrl, clone_dir: Path, token: str, api_url: str, branch: str):

    # Logic for cloning the repository into staged folder
    parts = str(repo_url._url).strip("/").split("/")
    org, repo = parts[3], parts[4].strip(".git")

    cloned_repo_dir: Path = clone_dir / repo

    if Path.exists(cloned_repo_dir):
        shutil.rmtree(cloned_repo_dir)
    else:
        Path.mkdir(cloned_repo_dir)

    headers = {
        "Authorization": "Bearer " + token
    }
    print("Cloning now...")
    def download_repo_contents(root_path_name: str, clone_path: Path):

        if not clone_path.exists():
            Path.mkdir(clone_path)
        
        github_url = f"{api_url}/repos/{org}/{repo}/contents/{root_path_name}?ref={branch}"
        print("here2")
        response = requests.get(
            url=github_url,
            headers=headers
        )

        if response.status_code != 200:
            print("ERROR OCCURED:", response.text)
            return
        
        repo_contents = response.json()

        if isinstance(repo_contents, list):
            
            for item in repo_contents:
                item_local_path = clone_path / item["name"]
                if item["type"] == "dir":
                    Path.mkdir(item_local_path)
                    item_path_name = f"{root_path_name}/{item["name"]}" if (root_path_name is not None and len(root_path_name) > 0) else item["name"]
                    download_repo_contents(root_path_name=item_path_name, clone_path=item_local_path)
                else:
                    download_file_contents(url=item["url"], clone_path=item_local_path)

    def download_file_contents(url: str, clone_path: Path):
        print("here")
        response = requests.get(
            url=url,
            headers=headers
        )

        if response.status_code != 200:
            print("ERROR OCCURED WHILE DOWNLOADING FILE:",response.text)
            return
        
        json_response = response.json()

        Path.touch(clone_path)
        Path.write_bytes(clone_path, base64.b64decode(json_response["content"]))

    download_repo_contents("", clone_path=cloned_repo_dir)

    return cloned_repo_dir

def get_root_project_dir():

    current = Path(__file__)

    pyproject_path = current / "pyproject.toml"
    if pyproject_path.exists():
        return current
    
    for parent in current.parents:

        pyproject_path = parent / "pyproject.toml"

        if pyproject_path.exists():
            return parent
    
    return None

def clone_repo(repo_url: HttpUrl, branch: str):
    root_dir = get_root_project_dir()
    print("got root directory at:",str(root_dir))
    clone_dir = root_dir / "staged"

    cloned_dir = clone(
        repo_url=repo_url,
        clone_dir=clone_dir,
        token=github_access_token,
        api_url=GITHUB_API_URL,
        branch=branch
    )

    return cloned_dir
