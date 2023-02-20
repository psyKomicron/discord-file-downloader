import logging
from discord import Client, Intents, Message
# This app
import src.config as config
from src.config import Config

logger = logging.getLogger(__name__)

async def on_message(message):
    logger.debug(message)

async def on_ready():
    logger.info("Client ready")


if __name__ == '__main__':
    logging.basicConfig(level=config.LOG_LEVEL)

    conf = Config()
    conf.openConfig()

    if config.DEBUG:
        def tab_print(s: str):
            print("\t{0}".format(s))
        conf.printOptions(tab_print)

    client = Client(intents = Intents.all())
    
    on_ready = client.event(on_ready)
    on_message = client.event(on_message)
    
    login = conf.getLogin()
    logger.info(login)
    client.run(login)