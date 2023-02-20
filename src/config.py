import genericpath
import json
import logging
import src.translations as translations
from src.translations import getString
import os
import re

# CONSTANTS
REPO_PATH="https://github.com/psyKomicron/discord-file-downloader"
VALID_FILES="\\.(jpg|png|bmp|gif|mp4|mp3|mov)$"
SHOW_TOKEN=False
LOG_LEVEL=logging.DEBUG
CONFIG_PATH="./config.json"
DEBUG=True


class Config:
    logger: logging.Logger = logging.getLogger(__name__)
    max_fetch_files: int = 0
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
    

    def openConfig(self):
        if genericpath.exists("./config.json"):
            rawJson = json.load(open("./config.json"))
            # Check config file to see if it is empty/defaulted.
            if len(set(rawJson.keys())) > 0 and len(set(rawJson.values())) > 0:
                # Configuration file is NOT empty.
                if self._loadConfig(rawJson):
                    self.logger.info("Config file is ok and loaded.")
                else:
                    self.logger.warning("Config file not ok, does not match required format")
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

        print(getString("read_full_doc").format(REPO_PATH))
        print(getString("starting_configuration"))

        # Ask user for login
        print(getString("checking_login"))
        passwd = self.getLogin()
        if not passwd:
            print("\t" + getString("token_is_empty"))
            
            if passwd == None:
                # Create secrets.json file
                open("./secrets.json", "x")
                self.logger.info("Created new secrets file (secrets.json)")

            passwd = input("\t" + getString("input_token"))
            name = input("\t" + getString("input_secret_name"))
            obj = { 
                "discord_client_secret": passwd, 
                "name": name
            }
            json.dump(obj, open("./secrets.json", "w"))
            self.secrets_file = "./secrets.json"
            
        elif SHOW_TOKEN or re.search(self.validationPattern, input(getString("check_token"))):
            print(getString("show_token").format(passwd))
            if not re.search(self.validationRe, input(getString("is_token_ok"))):
                passwd = input("\t" + getString("input_token"))
                name = input("\t" + getString("input_secret_name"))
                obj = { 
                    "discord_client_secret": passwd, 
                    "name": name
                }
                json.dump(obj, open("./secrets.json", "w"))    


        # Ask user for the download folder.
        currentPath = os.path.abspath("./downloads")
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
        if re.search(yesPattern, showAdvancedSettings):
            # Max fetch files.
            maxFetch = input(getString("max_fetch_files_name"))
            if not isinstance(maxFetch, int):
                print(getString("not_a_number"))
                raise Exception("Max fetch file is not a number.")
            #_updateConfig("max_fetch_files", maxFetch)
            self.max_fetch_files = maxFetch

            # Show unhandled messages.
            showUnhandledMessages = re.search(yesPattern, input(getString("show_unhandled_messages_name")))
            #_updateConfig("show_unhandled_messages", showUnhandledMessages)
            self.show_unhandled_messages = showUnhandledMessages

            # Exit on error
            exitOnError = re.search(yesPattern, input(getString("exit_on_error_name")))
            #_updateConfig("exit_on_error", exitOnError)
            self.exit_on_error = exitOnError

            # Show skips
            showSkips = re.search(yesPattern, input(getString("show_skips")))
            #_updateConfig("show_skips", showSkips)
            self.show_skips = showSkips

            # Exit after command
            exitAfterCommand = re.search(yesPattern, input(getString("exit_after_command_name")))
            #_updateConfig("exit_after_command", exitAfterCommand)
            self.exit_after_command = exitAfterCommand
        else:
            print("\t> " + getString("skipping_advanced_options"))
            # Set config defaults
            self.max_fetch_files = 1000
            self.show_unhandled_messages = False
            self.exit_on_error = True
            self.show_skips = False
            self.exit_after_command = True

        print(getString("printing_recap"))
        print(
            "\t" + getString("max_fetch_files_name") + f": {self.max_fetch_files}\n\t" +
            getString("show_unhandled_messages_name") + ": " + getString(f"{self.show_unhandled_messages}") + "\n\t" +
            getString("exit_on_error_name") + ": " + getString(f"{self.exit_on_error}") + "\n\t" + 
            getString("show_skips_name") + ": " + getString(f"{self.show_skips}") + "\n\t" +
            getString("exit_after_command_name") + ": " + getString(f"{self.exit_after_command}")
        )

        ok = re.search(yesPattern, input(getString("is_this_ok")))
        if ok:
            if not genericpath.exists(CONFIG_PATH):
                open(CONFIG_PATH, "x")

            file = open(CONFIG_PATH, "w")
            json.dump(self.toJson(), file)
            print(getString("config_saved"))
        else:
            print(getString("not_saving_config"))


    def getLogin(self):
        if genericpath.exists("./secrets.json"):
            secretsFile = json.load(open("./secrets.json"))
            if "discord_client_secret" in secretsFile:
                if "name" in secretsFile:
                    name = secretsFile["name"]
                    self.logger.debug(f"loading secret {name}")
                else:
                    self.logger.warning("secret is unnamed, it is possible that the secrets file does not have the correct format")

                secret = secretsFile["discord_client_secret"]
                if secret == None:
                    self.logger.critical("secrets file doesn't have secret, the app cannot login to Discord without it.")
                    #TODO: Raise exception to inform the user.

                return secret
        else:
            return None


    #def print_options():
        #for key in config:
         #   # print("{0} : {1}\n".format(get_string(key + "_name"), config[key]))
        #  print(f"{key} -> {config[key]}")

        pass


    def toJson(self):
        return {
            "max_fetch_files": self.max_fetch_files,
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
        template = {
            "max_fetch_files": 0,
            "show_unhandled_messages": False,
            "exit_on_error": True,
            "download_folder_path": "",
            "show_skips": False,
            "exit_after_command": False,
            "language": "",
            "secrets_file": ""
        }

        for attr in template:
            if attr in rawJson:
                self.attr = rawJson[attr]
                self.logger.debug(f"self.{attr}: {self.attr}")
            else:
                self.logger.warning(f"Config is missing attribute {attr}, cannot load configuration file from JSON.")
                return False
            # If we reach here, then the config file has been loaded properly.

        self.logger.debug("Self dict is empty")
        return True

    def getBool(self, config, key, default = False) -> bool:
        if key in config:
            value = config[key]  
            if isinstance(value, bool):
                return value == True

        return default