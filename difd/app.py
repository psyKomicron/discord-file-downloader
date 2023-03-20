import logging
import discord
import config
import console
import asyncio
from autoconfig import Config, checkNewRelease, AppVersion
from commands import CommandHandler
from config import DEBUG, __version__ as APP_VERSION, LOG_LEVEL


streamHandler = logging.StreamHandler()
streamHandler.setFormatter(console.ColorFormatter(fmt="%(levelname)-17s %(name)s  %(message)-7s"))
logging.basicConfig(level=LOG_LEVEL, handlers=[streamHandler])
logger = logging.getLogger("difd.main")

async def checkUpdates():
    update = await checkNewRelease()
    if update:
        currentAppVersion = AppVersion(version=APP_VERSION)
        if update.version > currentAppVersion:
            logger.info(f"New version available: {update.name} {update.version}")
    else:
        logger.debug("No packages released.")

# Main
if __name__ == '__main__':    
    print(f"Log level: {logging.getLevelName(LOG_LEVEL)}")
    # Check new version
    asyncio.run(checkUpdates())
    
    print(f"{config.APP_NAME} version {'.'.join(str(i) for i in config.__version__)}\n({config.REPO_PATH})")
    logger.info(f"<< Running discord.py version {discord.version_info.major}.{discord.version_info.minor}.{discord.version_info.micro} ({discord.version_info.releaselevel}) >>")
    conf = Config()
    conf.openConfig()

    if not conf.getToken():
        conf.setupToken()

    if config.DEBUG:
        def tab_print(s: str):
            print("\t-> {0}".format(s))
        conf.printOptions(tab_print)

    logger.info("Connecting...")

    login = conf.getToken()
    intents = discord.Intents(messages = True, guilds = True, message_content = True) 
    bot = CommandHandler(intents=intents, config=conf, logger=logging.getLogger("CommandHandler"))
    bot.run(token=login)