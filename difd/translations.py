import logging
import json
from discord.app_commands import Translator, locale_str, TranslationContextTypes
from discord import Locale
from typing import *


logger = logging.getLogger(__name__)

strings = json.load(open("./strings.json"))
langTag = "en-US"


def getString(tag: str) -> str:
    return strings[langTag][tag]


def setLanguage(languageTag):
    global langTag
    if languageTag in strings:
        langTag = languageTag
    else:
        raise IndexError("Language tag is not supported")


def getAvailableLanguagesSets():
    return strings.keys()


class Translator2(Translator):
    def __init__(self) -> None:
        super().__init__()


    async def translate(self, locale_string: locale_str, locale: Locale, context: TranslationContextTypes) -> Optional[str]:
        tag: str = locale.value
        string: str = locale_string.message
        if tag in strings and string in strings[tag]:
            return strings[tag][string]
        else:
            if locale not in strings:
                logger.warning(f"Translation request could not be fullfilled, locale '{locale}' is not supported")
                pass
            else:
                logger.warning(f"Translation request could not be fullfilled '{locale}' doesnt have {string}")
                pass

            return None