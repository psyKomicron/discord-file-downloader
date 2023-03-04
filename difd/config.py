__title__ = "DFiD"
__author__ = "psykomicron"
__version = (0, 0, 2)

import genericpath
import json
import logging
import translations
from translations import getString
import os
import re


# CONSTANTS
DEBUG=True

REPO_PATH="https://github.com/psyKomicron/discord-file-downloader"
"""Github repo."""

SHOW_TOKEN=False
"""Show discord connection token on startup."""

LOG_LEVEL=logging.DEBUG
"""Logging level."""

CONFIG_PATH="./config.json"
"""Configuration file path."""

SECRET_PATH="./secrets.json"
"""Discord token file path."""

APP_NAME="DFiD (Discord file downloader)"
"""Application name"""

RESOURCE_RE=re.compile(r"(https?: \/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", re.IGNORECASE)
"""Resource regex. Matches urls pointing to files."""

VALID_FILES_RE=re.compile(r"\\.(jpg|png|bmp|gif|mp4|mp3|mov)$", re.IGNORECASE)
"""Regex to check files extensions to find if the file should be downloaded."""

FILE_EXT_RE=re.compile(r'\.[A-z0-9]+$')
"""Regex to check if a string is a valid file name."""

HASH_FILENAMES=True
"""Whether or not to hash file names when downloading (can avoid collisions)."""


class Config:
    logger: logging.Logger = logging.getLogger(__name__)
    max_fetch_size: int = 0
    show_unhandled_messages: bool = False
    exit_on_error: bool = True
    download_folder_path: str = ""
    show_skips: bool = False
    exit_after_command: bool = False
    language: str = ""
    secrets_file: str = ""
    validationRe = re.compile("y|yes|true|false|oui|o", re.IGNORECASE)
        
    def __init__(self) -> None:
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
    

    def openConfig(self) -> None:
        if genericpath.exists(CONFIG_PATH):
            rawJson = json.load(open(CONFIG_PATH))
            # Check config file to see if it is empty/defaulted.
            if len(set(rawJson.keys())) > 0 and len(set(rawJson.values())) > 0:
                # Configuration file is NOT empty.
                if self._loadConfig(rawJson):
                    self.logger.info("Config file is ok and loaded.")
                    return
                else:
                    self.logger.warning("Config file not ok, does not match required format, starting configuration...")
            else:
                self.logger.critical("Config file is empty.")
                raise Exception()
            
        # The config file was empty, not existing or defaulted.
        print("Discord file downloader by psyKomicron\n -- Configuration --")

        availableLanguages = list(translations.getAvailableLanguagesSets())
        print(f"Available languages: {availableLanguages}")
        language = input("\tSelect app language: ") 
        chosenLanguage = "en-US"
        for item in availableLanguages:
            if re.search(item, language):
                chosenLanguage = item
                break
        translations.setLanguage(chosenLanguage)
        language = chosenLanguage

        print(getString("read_full_doc").format(REPO_PATH))
        print(getString("starting_configuration"))

        # Ask user for login
        self.setupToken()

        # Ask user for the download folder.
        currentPath = os.path.abspath("./difd/downloads")
        while True:
            downloadPath = input(getString("choose_download_folder").format(currentPath))
            if not downloadPath:
                downloadPath = currentPath
                print("\t> " + getString("using_default_download_folder"))
                break
            else:
                if genericpath.exists(downloadPath):
                    print("\t> " + getString("updated_download_folder").format(downloadPath))
                    break
                else:
                    print(getString("download_folder_not_found").format(downloadPath))
                    downloadPath = currentPath
        #_updateConfig("download_folder_path", currentPath)
        self.download_folder_path = downloadPath

        showAdvancedSettings = input(getString("show_advanced_settings"))
        if re.search(self.validationRe, showAdvancedSettings):
            # Max fetch files.
            maxFetch = input(getString("max_fetch_files_name"))
            if not isinstance(maxFetch, int):
                print(getString("not_a_number"))
                raise Exception("Max fetch file is not a number.")
            #_updateConfig("max_fetch_files", maxFetch)
            self.max_fetch_size = maxFetch

            # Show unhandled messages.
            showUnhandledMessages = re.search(self.validationRe, input(getString("show_unhandled_messages_name")))
            #_updateConfig("show_unhandled_messages", showUnhandledMessages)
            self.show_unhandled_messages = showUnhandledMessages

            # Exit on error
            exitOnError = re.search(self.validationRe, input(getString("exit_on_error_name")))
            #_updateConfig("exit_on_error", exitOnError)
            self.exit_on_error = exitOnError

            # Show skips
            showSkips = re.search(self.validationRe, input(getString("show_skips")))
            #_updateConfig("show_skips", showSkips)
            self.show_skips = showSkips

            # Exit after command
            exitAfterCommand = re.search(self.validationRe, input(getString("exit_after_command_name")))
            #_updateConfig("exit_after_command", exitAfterCommand)
            self.exit_after_command = exitAfterCommand
        else:
            print("\t> " + getString("skipping_advanced_options"))
            # Set config defaults
            self.max_fetch_size = 1000
            self.show_unhandled_messages = False
            self.exit_on_error = True
            self.show_skips = False
            self.exit_after_command = True

        print(getString("printing_recap"))
        print(
            "\t-" + getString("max_fetch_files_name") + f": {self.max_fetch_size}\n\t-" +
            getString("show_unhandled_messages_name") + ": " + getString(f"{self.show_unhandled_messages}") + "\n\t-" +
            getString("exit_on_error_name") + ": " + getString(f"{self.exit_on_error}") + "\n\t-" + 
            getString("show_skips_name") + ": " + getString(f"{self.show_skips}") + "\n\t-" +
            getString("exit_after_command_name") + ": " + getString(f"{self.exit_after_command}")
        )

        ok = re.search(self.validationRe, input(getString("is_this_ok")))
        if ok:
            if not genericpath.exists(CONFIG_PATH):
                open(CONFIG_PATH, "x")

            file = open(CONFIG_PATH, "w")
            json.dump(self.toJson(), file)
            print(getString("config_saved"))
        else:
            print(getString("not_saving_config"))


    def getToken(self) -> str:
        if genericpath.exists(SECRET_PATH):
            secretsFile = json.load(open(SECRET_PATH))
            if "discord_client_secret" in secretsFile:
                if "name" in secretsFile:
                    name = secretsFile["name"]
                    self.logger.info(f"Loading secret {name}")
                else:
                    self.logger.warning("Secret is unnamed, it is possible that the secrets file does not have the correct format")
                secret = secretsFile["discord_client_secret"]
                if secret == None:
                    self.logger.critical("Secrets file doesn't have secret, the app cannot login to Discord without it.")
                    #TODO: Raise exception to inform the user.
                return secret
        else:
            return None


    def setupToken(self) -> None:
        print(getString("checking_login"))
        passwd = self.getToken()
        if not passwd:
            print("\t" + getString("token_is_empty"))

            passWasNone = (passwd == None)
            passwd = input("\t" + getString("input_token"))
            while len(passwd) == 0:
                passwd = input("\t" + getString("input_token"))

            name = input("\t" + getString("input_secret_name"))
            if len(name) == 0:
                print("\tUnnamed")
                name = "Unnamed"

            obj = { 
                "discord_client_secret": passwd, 
                "name": name
            }

            if passWasNone:
                # Create secrets.json file
                open("./secrets.json", "x")
                self.logger.info("Created new secrets file (secrets.json)")
            
            json.dump(obj, open("./secrets.json", "w"))
            self.secrets_file = "./secrets.json"
            
        elif SHOW_TOKEN or re.search(self.validationRe, input(getString("check_token"))):
            print(getString("show_token").format(passwd))
            if not re.search(self.validationRe, input(getString("is_token_ok"))):
                passwd = input("\t" + getString("input_token"))
                name = input("\t" + getString("input_secret_name"))
                obj = { 
                    "discord_client_secret": passwd, 
                    "name": name
                }
                json.dump(obj, open("./secrets.json", "w"))    


    def toJson(self):
        return {
            "max_fetch_size": self.max_fetch_size,
            "show_unhandled_messages": self.show_unhandled_messages,
            "exit_on_error": self.exit_on_error,
            "download_folder_path": self.download_folder_path,
            "show_skips": self.show_skips,
            "exit_after_command": self.exit_after_command,
            "language": self.language,
            "secrets_file": self.secrets_file
        }


    def printOptions(self, printFunc):
        asJson = self.toJson()
        for key in asJson:
            printFunc(f"{key}: {asJson[key]}")


    def _loadConfig(self, rawJson):
        # Hard set attributes.
        if "max_fetch_size" in rawJson:
            self.max_fetch_size = rawJson["max_fetch_size"]
            pass
        if "show_unhandled_messages" in rawJson:
            self.show_unhandled_messages = rawJson["show_unhandled_messages"]
            pass
        if "exit_on_error" in rawJson:
            self.exit_on_error = rawJson["exit_on_error"]
            pass
        if "download_folder_path" in rawJson:
            self.download_folder_path = rawJson["download_folder_path"]
            pass
        if "show_skips" in rawJson:
            self.show_skips = rawJson["show_skips"]
            pass
        if "exit_after_command" in rawJson:
            self.exit_after_command = rawJson["exit_after_command"]
            pass
        if "language" in rawJson:
            self.language = rawJson["language"]
            pass
        if "secrets_file" in rawJson:
            self.secrets_file = rawJson["secrets_file"]
            pass

        # If we reach here, then the config file has been loaded properly.

        return True


    def getBool(self, config, key, default = False) -> bool:
        if key in config:
            value = config[key]  
            if isinstance(value, bool):
                return value == True

        return default