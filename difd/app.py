import logging
import discord
import config
import console
from autoconfig import Config
from commands import CommandHandler


streamHandler = logging.StreamHandler()
streamHandler.setFormatter(console.ColorFormatter(fmt="%(levelname)-17s %(name)s  %(message)-7s"))
logging.basicConfig(level=config.LOG_LEVEL, handlers=[streamHandler])

# Main
if __name__ == '__main__':    
    logger = logging.getLogger("difd.main")
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
    bot = CommandHandler(intents=intents, guild=289090423031463936, config=conf, logger=logging.getLogger("CommandHandler"))
    bot.run(token=login)