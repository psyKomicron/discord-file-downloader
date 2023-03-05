import os
import sys
import shutil
import importlib.util
import platform

REPO_PATH = "https://github.com/psyKomicron/discord-file-downloader"
            #"https://github.com/psyKomicron/discord-file-downloader.git"
SIMPLER_DOWNLOADER = True
DEBUG = True
PYTHON_PREFIX = "python3.11"
EXIT_ON_FAILED_DEPENDENCY_INSTALL = False
USE_GIT = False

def mkdir(path: str) -> bool:
    if os.name == "posix":
        if platform.system() == "Darwin":
            # MacOS
            pass
        if platform.system() == "Linux":
            return os.system(f"mkd  ir {path}") == 0
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
    

print("DiFD installer by psyKomicron")
downloadPath = ""
if input("Download in current directory ? [y/n] ") == "y":
    downloadPath = "./"
else:
    downloadPath = input("\tDesired path ? ")

if not os.path.exists(downloadPath):
    print(f"ERROR: {downloadPath} doesn't exists.")
    if input(f"Do you want to create {downloadPath} ? [y/n] ") == "y":
        mkdir(downloadPath)
    else:
        exit(-1)

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
            print("Successfully installed\n\t" + "\n\t- ".join(installedDeps))
else:
    checkInstall("curl")
    