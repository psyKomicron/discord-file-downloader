import os

def getEnvVar(name: str, default: str = "") -> str:
    if name in os.environ:
        return os.environ[name]
    return ""

def getEnvBool(name: str, default: bool = False) -> str:
    return getEnvVar(name) == "True"

    