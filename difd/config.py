__title__ = "DFiD"
__author__ = "psykomicron"
__version__ = (0, 0, 4)

import logging
import re
import confighelper as helper

DEBUG=helper.getEnvBool("DEBUG")
SHOW_TOKEN=helper.getEnvBool("SHOW_TOKEN")
"""Show discord connection token on startup."""
# logging.DEBUG if DEBUG else logging.INFO
LOG_LEVEL=logging._levelToName[helper.getEnvVar("L")] if helper.getEnvVar("L") in logging._levelToName else logging.INFO
"""Logging level."""
CONFIG_PATH="./config.json"
"""Configuration file path."""
SECRET_PATH="./secrets.json"
"""Discord token file path."""
HASH_FILENAMES=helper.getEnvBool("HASH_FILENAMES", True)
"""Whether or not to hash file names when downloading (can avoid collisions)."""

# CONSTANTS
DEPENDENCIES = ["aiohttp", "discord.py", "aiofiles"]
REPO_PATH="https://github.com/psyKomicron/discord-file-downloader"
API_URL = "https://api.github.com/repos/psykomicron/discord-file-downloader/releases/latest"
APP_NAME="DFiD (Discord file downloader)"
"""Application name"""
RESOURCE_RE=re.compile(r"(https?: \/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", re.IGNORECASE)
"""Resource regex. Matches urls pointing to files."""
VALID_FILES_RE=re.compile(r".*(\\.jpg|png|bmp|gif|mp4|mp3|mov)$", re.IGNORECASE)
"""Regex to check files extensions to find if the file should be downloaded."""
FILE_EXT_RE=re.compile(r'\.[A-z0-9]+$')
"""Regex to check if a string is a valid file name."""