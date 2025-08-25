import os
import shutil
import json

default_cmods_json_structure = {"repositories":{}, "dependencies":{}, "CFLAGS":""}

def init_project():
    if "src" not in os.listdir("."):
        os.mkdir("src")
    if "include" not in os.listdir("."):
        os.mkdir("include")
    if "build" not in os.listdir("src"):
        os.mkdir("src/build")

    with open("cmods.json", "w") as f:
        json.dump(default_cmods_json_structure, f)
