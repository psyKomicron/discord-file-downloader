import logging
from logging import debug
import json

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