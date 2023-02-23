import logging
import discord
# This app
import difd.config as config
from difd.config import Config
from difd.commands import CommandHandler


logging.basicConfig(format="%(levelname)s  %(name)-12s  %(message)-8s  ", level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Main
if __name__ == '__main__':    
    print(f"{config.APP_NAME}\n({config.REPO_PATH})")
    print(f">> Running discord.py version {discord.version_info.major}.{discord.version_info.minor}.{discord.version_info.micro} ({discord.version_info.releaselevel})")

    conf = Config()
    conf.openConfig()

    if not conf.getToken():
        conf.setupToken()

    if config.DEBUG:
        def tab_print(s: str):
            print("\t-> {0}".format(s))
        conf.printOptions(tab_print)

    logger.info("Connecting...")
    input("")

    login = conf.getToken()
    intents = discord.Intents(messages = True, guilds = True, message_content = True) 
    bot = CommandHandler(intents=intents, guild=289090423031463936, config=conf, logger=logging.getLogger("CommandHandler"))
    bot.run(token=login)