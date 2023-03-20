#!/usr/bin/env python3
"""
    Standalone installer and updater.
"""
__title__ = "DFiD Installer"
__author__ = "psykomicron"
__version__ = (1, 0, 1)

import os
import sys
import shutil
import json
import urllib3
import importlib.util
import platform
import os
import io
import json
from os import path, mkdir
from typing import Any
from io import BytesIO

def getEnvVar(name: str | list[str], default: str = "") -> str:
    if isinstance(name, str):
        if name in os.environ:
            return os.environ[name]
    elif isinstance(name, list):
        for n in name:
            if n in os.environ:
                return os.environ[name]
    return default

def getEnvBool(name: str, default: bool = False) -> str:
    return name in os.environ and getEnvVar(name) != "False"

SIMPLER_DOWNLOADER  = getEnvBool("SIMPLER_DOWNLOADER", True)
DEBUG               = getEnvBool("DEBUG", False)
PYTHON_PREFIX       = getEnvVar(["PY", "PYTHON_PREFIX"], "python3.11")
USE_GIT             = getEnvBool("USE_GIT", False)
EXIT_ON_FAILED_DEPENDENCY_INSTALL = False
REPO_PATH = "https://github.com/psyKomicron/discord-file-downloader"
API_URL = "https://api.github.com/repos/psykomicron/discord-file-downloader/releases/latest"
    
def checkInstall(command: str) -> None:
    shpath = shutil.which(command)
    if not shpath or len(shpath) == 0:
        print(f"{command} is not installed, install it and rerun the installation script.")
        if os.name != "posix":
            exit()
        if tryInput("Do you want to install {command} ?"):
            exit()
        if os.system(f"sudo apt install {command}") != 0:
            print(f"Failed to install {command}.")
            exit()    
        print(f"Successfully installed {command}.")
    
def installDependencies(configPyPath: str) -> None:
    # Check if pip is installed.
    if os.system(f"{PYTHON_PREFIX} -m pip") != 0:
        # Check if "ensurepip" script is available.
        if os.system(f"{PYTHON_PREFIX} -m ensurepip") != 0:
            if os.system(f"curl -LJO \"https://bootstrap.pypa.io/get-pip.py\"") != 0:
                print(f"pip is not installed and is required to run python. Please install it.")
                exit(-3)
            elif os.system(f"{PYTHON_PREFIX} get-pip.py") != 0 or os.system(f"{PYTHON_PREFIX} -m pip") != 0:
                print(f"Failed to install pip using bootstrap script.")
                exit(-3)
            else:
                print(f"Succesfully installed pip. Module installation can proceed.")
        else:
            print(f"Successfully installed pip using ensurepip module.")
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
        else:
            installedDeps.append(dependency)
    if len(installedDeps) != len(dependencies):
        print("Missing dependencies:")
        for dep in dependencies:
            if dep not in installedDeps:
                print(f"    - {dep}")
    elif len(installedDeps) == 0:
        print(f"Nothing installed. Check you internet connection or try the installation steps manually.")
    else:
        print("Successfully installed:\n - " + "\n - ".join(installedDeps))

def tryInput(message: str) -> bool:
    try:
        res = input(f"{message} [y/n]: ")
        return res in ["y", "yes"]
    except:
        exit()

def installLatest(downloadPath: str):
    checkInstall("curl")
    if not path.exists(downloadPath):
        mkdir(downloadPath)
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
    if not os.path.exists(fileName):
        print(f"{fileName} doesn't exists.")
        exit(-1)
    print(f"Unpacking {fileName}...")
    shutil.unpack_archive(fileName, "./difd")
    os.chdir("./difd/")
    installDependencies("config.py")
    os.chdir("../")
    # Clean up
    os.remove(f"{fileName}")

def update() -> bool:
    if path.exists("./difd"):
        # App already exists. Choose whether to download it again/update or not.
        if DEBUG or tryInput("Application already installed, do you want to update it ?"):
            currentPath = path.abspath("./")
            if path.exists("./difd.old/"):
                os.remove("./difd.old/")
            # Rename old install.
            os.rename("./difd", "difd.old")
            installLatest(currentPath)
            # Copy config files to new installation directory.
            config = None
            secret = ["", ""]
            if path.exists("./difd.old/config.json"):
                with open("./difd.old/config.json") as fp:
                    config = json.load(fp)
                    print(f"Config\n: {config}")
            if path.exists("./difd.old/secrets.json"):
                with open("./difd.old/secrets.json") as fp:
                    secretsJson = json.load(fp)
                    if not isinstance(secretsJson, list) and "discord_client_secret" in secretsJson:
                        secret[0] = secretsJson["discord_client_secret"]
                        secret[1] = secretsJson["name"]
                        print(f"{secret[1]} - {secret[0]}")

            if input("Do you want to start the app ? [y/n] ") == "y":
                print("Bye bye ! :)\n")
                os.system(f"{PYTHON_PREFIX} app.py")
            else:
                print("Bye bye ! :)")
            return True
    return False

    
def main():
    if update():
        exit()

    downloadPath = ""
    if input("Download in current directory ? [y/n] ") == "n":
        downloadPath = input("\tDesired path ? ")
    else:
        downloadPath = "./"

    if not os.path.exists(downloadPath):
        print(f"ERROR: {downloadPath} doesn't exists.")
        if input(f"Do you want to create {downloadPath} ? [y/n] ") == "y":
            if not mkdir(downloadPath):
                exit(-2)
        else:
            exit(-1)
    elif DEBUG and downloadPath != "./":
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
        installLatest(downloadPath)
        if input("Do you want to start the app ? [y/n] ") == "y":
            print("Bye bye ! :)\n")
            os.system(f"{PYTHON_PREFIX} app.py")
        else:
            print("Bye bye ! :)")
    
    
if __name__ == "__main__":
    if DEBUG:
        print("DiFD installer by psyKomicron [DEBUG MODE]")
        print(path.abspath("./"))
    else:
        print("DiFD installer by psyKomicron")
    main()