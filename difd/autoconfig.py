import os
import re
import json
import logging
import genericpath
import translations
import asyncio
import io
from typing import Tuple, Any
from translations import getString
from config import CONFIG_PATH, SECRET_PATH, REPO_PATH, SHOW_TOKEN, API_URL
from aiohttp import ClientSession, ClientTimeout, ClientResponse

class Config:
    logger: logging.Logger = logging.getLogger("difd.config")
    max_fetch_size: int = 0
    show_unhandled_messages: bool = False
    exit_on_error: bool = True
    download_folder_path: str = ""
    show_skips: bool = False
    exit_after_command: bool = False
    language: str = ""
    secrets_file: str = ""
    allowed_users: list[str] = []
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
                try:
                    self._loadConfig(rawJson)
                    self.logger.info("Config file is ok and loaded.")
                    return
                except:
                    self.logger.warning("Config file not ok, does not match required format, starting configuration...")
            else:
                self.logger.critical("Config file is empty.")
                raise Exception()
        # The config file was empty, not existing or defaulted.
        print("-- Configuration --")
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
        # Ask user for login:
        self.setupToken()
        # Ask user for the download folder:
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
        self.download_folder_path = downloadPath
        # Configure allowed users:
        if self.validationRe.search(input(getString("configure_allowed_users"))):
            allowedUsers = input(getString("input_allowed_users"))
            if len(allowedUsers) > 0:
                users = allowedUsers.split(' ')
                if len(users) > 0:
                    discordNameRe = re.compile("[A-z]+#[0-9]+")
                    for user in users:
                        if discordNameRe.match(user):
                            self.allowed_users.append(user)
                        else:
                            print(getString("invalid_discord_username").format(user))
                else:
                    pass
        showAdvancedSettings = input(getString("show_advanced_settings"))
        if re.search(self.validationRe, showAdvancedSettings):
            # Max fetch files.
            maxFetch = input(getString("max_fetch_files_name"))
            if not isinstance(maxFetch, int):
                print(getString("not_a_number"))
                raise Exception("Max fetch file is not a number.")
            self.max_fetch_size = maxFetch
            # Show unhandled messages.
            showUnhandledMessages = re.search(self.validationRe, input(getString("show_unhandled_messages_name")))
            self.show_unhandled_messages = showUnhandledMessages
            # Exit on error
            exitOnError = re.search(self.validationRe, input(getString("exit_on_error_name")))
            self.exit_on_error = exitOnError
            # Show skips
            showSkips = re.search(self.validationRe, input(getString("show_skips")))
            self.show_skips = showSkips
            # Exit after command
            exitAfterCommand = re.search(self.validationRe, input(getString("exit_after_command_name")))
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
            getString("exit_after_command_name") + ": " + getString(f"{self.exit_after_command}") +
            getString("allowed_users") + ": " + " ".join(self.allowed_users)
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
        #if "max_fetch_size" in rawJson:
        self.max_fetch_size = rawJson["max_fetch_size"]
        #if "show_unhandled_messages" in rawJson:
        self.show_unhandled_messages = rawJson["show_unhandled_messages"]
        #if "exit_on_error" in rawJson:
        self.exit_on_error = rawJson["exit_on_error"]
        #if "download_folder_path" in rawJson:
        self.download_folder_path = rawJson["download_folder_path"]
        #if "show_skips" in rawJson:
        self.show_skips = rawJson["show_skips"]
        #if "exit_after_command" in rawJson:
        self.exit_after_command = rawJson["exit_after_command"]
        #if "language" in rawJson:
        self.language = rawJson["language"]
        #if "secrets_file" in rawJson:
        self.secrets_file = rawJson["secrets_file"]
        #if "allowed_users" in rawJson:
        self.allowed_users = rawJson["allowed_users"]


    def getBool(self, config, key, default = False) -> bool:
        if key in config:
            value = config[key]  
            if isinstance(value, bool):
                return value == True

        return default
    

class Asset:
    fileName: str
    contentType: str
    downloadUrl: str
    
    def __init__(self, _fileName, _contentType, _downloadUrl) -> None:
        self.fileName = _fileName
        self.contentType = _contentType
        self.downloadUrl = _downloadUrl


class AppVersion:
    major: int = -1
    minor: int = -1
    revision: int = -1

    def __init__(self, version: list[int] = None, major = None, minor = None, revision = None) -> None:
        if version:
            if len(version) == 3:
                self.major, self.minor, self.revision = version
            else:
                self.major = version[0]
                self.minor = version[1] if len(version) > 1 else -1
                self.revision = version[2] if len(version) > 2 else -1
        else:
            self.major = major
            self.minor = minor
            self.revision = revision

    def __eq__(self, other) -> bool:
        return (self.major == other.major) and (self.minor == other.minor) and (self.revision == other.revision)
    
    def __lt__(self, other) -> bool:
        if self.major < other.major:
            return True
        elif self.major > other.major:
            return False
        if self.minor < other.minor:
            return True
        elif self.minor > other.minor:
            return False
        if self.revision < other.revision:
            return True
        elif self.revision > other.revision:
            return False
        return False
    
    def __gt__(self, other) -> bool:
        # Check major.
        if self.major > other.major:
            return True
        elif self.major < other.major:
            return False
        # Check minor.
        if self.minor > other.minor:
            return True
        elif self.minor < other.minor:
            return False
        # Check revision.
        if self.revision > other.revision:
            return True
        elif self.revision < other.revision:
            return False
        return False
    
    def pack(self) -> list[int]:
        return [self.major, self.minor, self.revision]


class UpdateContext:
    tag: str = None
    version: AppVersion
    name: str = None
    assets: list[Asset] = []
    notes: str = ""

    def __init__(self, rawJson: Any) -> None:
        self.tag = rawJson["tag_name"]
        self._tryParseTag()
        self.name = rawJson["name"]
        assets = rawJson["assets"]
        if len(assets) > 0:
            # Assets available
            for asset in assets:
                fileName = asset["name"]
                contentType = asset["content_type"]
                downloadUrl = asset["browser_download_url"]
                self.assets.append(Asset(fileName, contentType, downloadUrl))
        self.notes = rawJson["body"]

    def _tryParseTag(self):
        if not self.tag.startswith('v'):
            return
        tag = self.tag[1:]
        tag = tag.split('.')
        ints = []
        for part in tag:
            try:
                ints.append(int(part))
            except:
                pass
        self.version = AppVersion(version=ints)

    def _printAssets(self) -> str:
        assetsNames = []
        for asset in self.assets:
            assetsNames.append(f" - {asset.fileName}")
        return "\n".join(assetsNames)

    def __str__(self) -> str:
        return f"""
    Release {self.name} ({self.tag}):
Assets:
{self._printAssets()}
Notes (Markdown):
{self.notes}
"""
    

async def checkNewRelease() -> UpdateContext:
    logger = logging.getLogger("checkNewRelease")
    async with ClientSession() as session:
        async with session.get(API_URL) as resp:
            if resp.status != 200:
                match resp.status:
                    case 404:
                        logger.info(f"No release available for this app. {API_URL}")
                    case 403:
                        logger.warning(f"GitHub response was 403 for {API_URL}")
                    case _:
                        logger.debug(f"Response status not recognized: {resp.status}")
                return None
            auto = io.BytesIO(await resp.content.read())
            jason = json.load(auto)
            update = UpdateContext(jason)
            if len(update.assets) > 0:
                return update
            return None
