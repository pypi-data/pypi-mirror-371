import json

def cmods_repo_add(name, url):
    cmods_config = None
    
    with open("cmods.json", "r") as f:
        cmods_config = json.load(f)
    
    cmods_config["repositories"][name]=url
    
    with open("cmods.json", "w") as f:
        json.dump(cmods_config, f)

def cmods_repo_del(name):
    cmods_config = None
    
    with open("cmods.json", "r") as f:
        cmods_config = json.load(f)
    
    del cmods_config["repositories"][name]
    
    with open("cmods.json", "w") as f:
        json.dump(cmods_config, f)

def cmods_mod_add(name, repo):
    cmods_config = None
    
    with open("cmods.json", "r") as f:
        cmods_config = json.load(f)
    
    cmods_config["dependencies"][name]=repo
    
    with open("cmods.json", "w") as f:
        json.dump(cmods_config, f)

def cmods_mod_del(name):
    cmods_config = None
    
    with open("cmods.json", "r") as f:
        cmods_config = json.load(f)
    
    del cmods_config["dependencies"][name]
    
    with open("cmods.json", "w") as f:
        json.dump(cmods_config, f)

def cmods_set_cflags(cflags):
    cmods_config = None
    
    with open("cmods.json", "r") as f:
        cmods_config = json.load(f)
    
    cmods_config["CFLAGS"]=cflags
    
    with open("cmods.json", "w") as f:
        json.dump(cmods_config, f)
