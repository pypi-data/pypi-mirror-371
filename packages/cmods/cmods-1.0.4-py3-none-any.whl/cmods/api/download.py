import os
import shutil
import zipfile
import io
import requests

def cmods_download(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(".")
    except Exception:
        print("[ Error ]")
        return False
    return True

def cmods_from_repo(repo_url, name):
    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        return cmods_download(response.json()[name])
    except Exception:
        print(f"[ Error downloading {name} from {repo_url} ]")
        return False
