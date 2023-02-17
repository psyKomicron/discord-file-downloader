import genericpath
import json
import logging
from logging import warning, debug, critical
import src.translations as translations
from src.translations import get_string
import os
import re

# CONSTANTS
REPO_PATH="https://github.com/psyKomicron/discord-file-downloader"
VALID_FILES="\\.(jpg|png|bmp|gif|mp4|mp3|mov)$"
SHOW_TOKEN=False
LOG_LEVEL=logging.DEBUG
CONFIG_PATH="./config.json"
DEBUG=True

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

def get_bool(config, key, default = False) -> bool:
    if key in config:
        value = config[key]  
        if isinstance(value, bool):
            return value == True

    return default
        

def open_config():
    if genericpath.exists("./config.json"):
        try:
            conf = json.load(open("./config.json"))
            
            # Check config file to see if it is empty/defaulted.
            if len(set(conf.keys())) > 0 and len(set(conf.values())) > 0:
                # Configuration file is NOT empty.
                logging.info("Config file is ok.")
                return conf 

        except json.decoder.JSONDecodeError as ex:
            debug(ex)

    configFile = ConfigFileTemplate()
        
    # The config file was empty, not existing or defaulted.
    print("Discord file downloader by psyKomicron")

    availableLanguages = list(translations.getAvailableLanguagesSets())
    print(availableLanguages)
    print(f"Available languages: {availableLanguages}")
    language = input("\tSelect app language: ") 
    chosenLanguage = "en-US"
    for item in availableLanguages:
        if re.search(item, language):
            chosenLanguage = item
            break
    translations.setLanguage(chosenLanguage)

    print(get_string("read_full_doc").format(REPO_PATH))
    print(get_string("starting_configuration"))

    # Ask user for login
    print(get_string("checking_login"))
    passwd = get_login()
    if not passwd:
        print("\t" + get_string("password_is_empty"))
        
        if passwd == None:
            # Create secrets.json file
            open("./secrets.json", "x")
            logging.info("Created new secrets file (secrets.json)")

        passwd = input("\t" + get_string("input_password"))
        name = input("\t" + get_string("input_secret_name"))
        obj = { 
            "discord_client_secret": passwd, 
            "name": name
        }
        json.dump(obj, open("./secrets.json", "w"))
        
        #_updateConfig("secret_file", "./secrets.json")
        configFile.secrets_file = "./secrets.json"
    elif SHOW_TOKEN:
        print(get_string("show_token").format(passwd))

    # Ask user for the download folder.
    currentPath = os.path.abspath("./downloads")
    while True:
        downloadPath = input(get_string("choose_download_folder").format(currentPath))
        if not downloadPath:
            downloadPath = currentPath
            print("\t> " + get_string("using_default_download_folder"))
            break
        else:
            if genericpath.exists(downloadPath):
                print("\t> " + get_string("updated_download_folder").format(downloadPath))
                break
            else:
                print(get_string("download_folder_not_found").format(downloadPath))
                downloadPath = currentPath
    #_updateConfig("download_folder_path", currentPath)
    configFile.download_folder_path = downloadPath

    yesPattern = re.compile("y|yes|true|false|oui|o", re.IGNORECASE)
    showAdvancedSettings = input(get_string("show_advanced_settings"))
    if re.search(yesPattern, showAdvancedSettings):
        # Max fetch files.
        maxFetch = input(get_string("max_fetch_files_name"))
        if not isinstance(maxFetch, int):
            print(get_string("not_a_number"))
            raise Exception("Max fetch file is not a number.")
        #_updateConfig("max_fetch_files", maxFetch)
        configFile.max_fetch_files = maxFetch

        # Show unhandled messages.
        showUnhandledMessages = re.search(yesPattern, input(get_string("show_unhandled_messages_name")))
        #_updateConfig("show_unhandled_messages", showUnhandledMessages)
        configFile.show_unhandled_messages = showUnhandledMessages

        # Exit on error
        exitOnError = re.search(yesPattern, input(get_string("exit_on_error_name")))
        #_updateConfig("exit_on_error", exitOnError)
        configFile.exit_on_error = exitOnError

        # Show skips
        showSkips = re.search(yesPattern, input(get_string("show_skips")))
        #_updateConfig("show_skips", showSkips)
        configFile.show_skips = showSkips

        # Exit after command
        exitAfterCommand = re.search(yesPattern, input(get_string("exit_after_command_name")))
        #_updateConfig("exit_after_command", exitAfterCommand)
        configFile.exit_after_command = exitAfterCommand
    else:
        print("\t> " + get_string("skipping_advanced_options"))
        # Set config defaults
        configFile.max_fetch_files = 1000
        configFile.show_unhandled_messages = False
        configFile.exit_on_error = True
        configFile.show_skips = False
        configFile.exit_after_command = True

    print(get_string("printing_recap"))
    print(
        "\t" + get_string("max_fetch_files_name") + f": {configFile.max_fetch_files}\n\t" +
        get_string("show_unhandled_messages_name") + ": " + get_string(f"{configFile.show_unhandled_messages}") + "\n\t" +
        get_string("exit_on_error_name") + ": " + get_string(f"{configFile.exit_on_error}") + "\n\t" + 
        get_string("show_skips_name") + ": " + get_string(f"{configFile.show_skips}") + "\n\t" +
        get_string("exit_after_command_name") + ": " + get_string(f"{configFile.exit_after_command}")
    )

    ok = re.search(yesPattern, input(get_string("is_this_ok")))
    if ok:
        if not genericpath.exists(CONFIG_PATH):
            open(CONFIG_PATH, "x")

        file = open(CONFIG_PATH, "w")
        json.dump(configFile.to_json(), file)
        print(get_string("config_saved"))
    else:
        print(get_string("not_saving_config"))


def get_login():
    if genericpath.exists("./secrets.json"):
        secretsFile = json.load(open("./secrets.json"))
        if "discord_client_secret" in secretsFile:
            if "name" in secretsFile:
                name = secretsFile["name"]
                debug(f"loading secret {name}")
            else:
                warning("secret is unnamed, it is possible that the secrets file does not have the correct format")

            secret = secretsFile["discord_client_secret"]
            if secret == None:
                critical("secrets file doesn't have secret, the app cannot login to Discord without it.")
                #TODO: Raise exception to inform the user.

            return secret
    else:
        return None


def print_options(_config = None):
    config = _config
    if not config:
        config = json.load(open(CONFIG_PATH))

    for key in config:
        # print("{0} : {1}\n".format(get_string(key + "_name"), config[key]))
        print(f"{key} -> {config[key]}")

def startHelp(config):
    pass


class ConfigFileTemplate:
    max_fetch_files: int = 0
    show_unhandled_messages: bool = False
    exit_on_error: bool = True
    download_folder_path: str = ""
    show_skips: bool = False
    exit_after_command: bool = False
    language: str = ""
    secrets_file: str = ""

    def to_json(self):
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