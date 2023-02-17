import genericpath
from logging import warning, debug, critical
from src.translations import getString

def checkConfigFile(config) -> bool:
    return True


def getLogin():
    if genericpath.exists("./secrets.json"):
        secretsFile = open("./secrets.json")
        name = secretsFile[name]
        secret = secretsFile["discord_client_secret"]

        if name == None:
            warning("secret is unnamed, it is possible that the secrets file does not have the correct format")
        else:
            debug(f"loading secret {name}")

        if secret == None:
            critical("secrets file doesn't have secret, the app cannot login to Discord without it.")
            #TODO: Raise exception to inform the user.

        return secret
             
    else:
        return None


def startHelp(config):
    print("Discord file downloader by psyKomicron")
    print(getString("read_full_doc").format(config["repo_path"]))

    print(getString("checking_login"))
    
    passwd = getLogin()
    if len(passwd) == 0:
        print(getString("password_is_empty"))

    pass