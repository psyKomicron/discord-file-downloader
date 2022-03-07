import json
from LocalClient import LocalClient

client = LocalClient()

secretsFile = open("./secrets.json")

if secretsFile is not None:
    secrets = json.load(secretsFile)
    login = secrets['discord_client_secret']
    client.run(login)
else:
    print("No loggin found for the bot, exiting")
