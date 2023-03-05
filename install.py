import os
import sys
import shutil
import json
import urllib3
import importlib.util
import platform
import os
import io

REPO_PATH = "https://github.com/psyKomicron/discord-file-downloader"
            #"https://github.com/psyKomicron/discord-file-downloader.git"
SIMPLER_DOWNLOADER = True
DEBUG = True
PYTHON_PREFIX = "python3.11"
EXIT_ON_FAILED_DEPENDENCY_INSTALL = False
USE_GIT = False
API_URL = "https://api.github.com/repos/psykomicron/discord-file-downloader/releases/latest"

def mkdir(path: str) -> bool:
    if os.name == "posix":
        if platform.system() == "Darwin":
            # MacOS
            pass
        if platform.system() == "Linux":
            return os.system(f"mkdir {path}") == 0
    else:
        return False
    
def checkInstall(command: str) -> None:
    shpath = shutil.which(command)
    if not shpath or len(shpath) == 0:
        print(f"{command} is not installed, install it and rerun the installation script.")
        if os.name != "posix":
            exit()
        if input(f"Do you want to install {command} ? [y/n] ") == "n":
            exit()

        if os.system(f"sudo apt install {command}") != 0:
            print(f"Failed to install {command}.")
            exit()    
        print(f"Successfully installed {command}.")
    
def installDependencies(configPyPath: str) -> None:
    spec = importlib.util.spec_from_file_location("config", configPyPath)
    config = importlib.util.module_from_spec(spec)
    sys.modules["config"] = config
    spec.loader.exec_module(config)
    dependencies: list[str] = config.DEPENDENCIES
    print("Installing required packages...")
    print(f"Using {PYTHON_PREFIX}")
    installedDeps = []
    for dependency in dependencies:
        print(f"Installing {dependency}...")
        if os.system(f"{PYTHON_PREFIX} -m pip install {dependency}") != 0:
            print(f"Failed to install {dependency}, you will need to install it before running DiFD.")
            if EXIT_ON_FAILED_DEPENDENCY_INSTALL: exit(-1)
        installedDeps.append(dependency)
    if len(installedDeps) != len(dependencies):
        print("Missing dependencies:")
        for dep in dependencies:
            if dep not in installedDeps:
                print(f"\t- {dep}")
    elif len(installedDeps) == 0:
        print(f"Nothing installed. Check you internet connection or try the installation steps manually.")
    else:
        print("Successfully installed:\n - " + "\n - ".join(installedDeps))


print("DiFD installer by psyKomicron")
downloadPath = ""
if input("Download in current directory ? [y/n] ") == "n":
    downloadPath = input("\tDesired path ? ")
else:
    downloadPath = "./test/"

if not os.path.exists(downloadPath):
    print(f"ERROR: {downloadPath} doesn't exists.")
    if input(f"Do you want to create {downloadPath} ? [y/n] ") == "y":
        if not mkdir(downloadPath):
            exit(-2)
    else:
        exit(-1)
elif DEBUG:
    if input("Do you want to clean output directory ? [y/n] ") == "y":
        os.rmdir(downloadPath)
        if not mkdir(downloadPath): 
            exit(-2)

if USE_GIT:
    checkInstall("git")
    print("Cloning repository...")
    if not DEBUG and os.system(f"git clone {REPO_PATH}.git {downloadPath}") != 0:
        print("Failed to clone repository, please check you internet connection and retry installation.")
        exit(-1)
    print(f"Cloned repository into {downloadPath}")
    if SIMPLER_DOWNLOADER:
        print("Switching to branch simpler-downloader...")
        os.chdir(downloadPath)
        # current path './test/'
        if not DEBUG and os.system("git checkout simpler-downloader") != 0:
            print("Failed checkout, impossible to use branch 'simpler-downloader'")
            exit(-1)
        print("Switched to branch simpler-downloader")
        currentPath = os.path.join("./", "difd")
        os.chdir(currentPath)
        print("Checking config.py for dependencies...")
        configPyPath = "config.py"
        if not os.path.exists(configPyPath):
            print(f"{configPyPath} not found, impossible to download dependencies.")
            exit(-1)
        # Dynamic import for config.py
        installDependencies(configPyPath)        
else:
    os.chdir(downloadPath)
    print(f"Current dir: {os.path.abspath('./')}")
    checkInstall("curl")
    # Perform GET request.
    http = urllib3.PoolManager()
    r = http.request("GET", API_URL)
    if r.status != 200:
        print("Failed to contact GitHub API to get latest DiFD release.")
        exit(-1)
    response = json.load(io.BytesIO(r.data))
    if "assets" not in response:
        print("Not assets found in latest release, nothing to download.")
        exit()
    tag = response["tag_name"]
    name = response["name"]
    assets = response["assets"]
    asset = assets[0]
    fileName = asset["name"]
    contentType = asset["content_type"]
    downloadUrl = asset["browser_download_url"]
    print(f"Downloading latest release ({name} {tag})...")
    os.system(f"curl -LJO {downloadUrl}")
    #r = http.request("GET", downloadUrl)
    #if r.status != 200:
    #    print("Failed to download latest DiFD release.")
    #    exit(-1)
    if not os.path.exists(fileName):
        print(f"{fileName} doesn't exists.")
        exit(-1)
    print(f"Unpacking {fileName}...")
    shutil.unpack_archive(fileName)
    os.chdir(f"./{fileName[:-4]}/difd/")
    installDependencies("config.py")
    if input("Do you want to start the app ? [y/n]") == "y":
        os.system(f"{PYTHON_PREFIX} app.py")
    else:
        print("Bye bye ! :)")
    