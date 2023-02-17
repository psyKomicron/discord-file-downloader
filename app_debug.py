import logging
import sys
import json
from logging import *
# This app
from src.config import *
from src.translations import getString


def startHelp(config):
    print("Discord file downloader by psyKomicron")
    print(getString("read_full_doc").format(config["repo_path"]))

    print(getString("checking_login"))
    passwd = getLogin()
    if len(passwd) == 0:
        print(getString("password_is_empty"))

    pass


if __name__ == '__main__':
    # Set log level to debug.
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        config = json.load(open("./config.json"))
        if not checkConfigFile(config):
            raise Exception("Config is malformed")
    
        if len(sys.argv) == 3:
            try:
                pass
            except Exception as ex:
                print(f"Failed to login: \n\t{ex}")

        else:
            if len(sys.argv) < 3:
                # TODO: Run command line help
                startHelp()
                pass
            elif len(sys.argv) > 3:
                # TODO: Print command line help (user considered power user). 
                print("Too many options.")

    except Exception as ex:
        critical("Config file is malformed or absent. Please check installation.")
        debug(f"Exception: {ex}")