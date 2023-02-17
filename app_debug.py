import logging
from discord import Client, Intents, Message
# This app
import src.config as config

logger = logging.getLogger(__name__)

async def on_message(message):
    logger.debug(message)

async def on_ready():
    logger.info("Client ready")


if __name__ == '__main__':
    logging.basicConfig(level=config.LOG_LEVEL)

    conf = config.open_config()
    if config.DEBUG:
        config.print_options(conf)

    try:
        client = Client(intents = Intents.all())
        
        on_ready = client.event(on_ready)
        on_message = client.event(on_message)
        
        login = config.get_login()
        logger.info(login)
        client.run(login)

    except Exception as ex:
        print(f"Failed to login: \n\t{ex}")