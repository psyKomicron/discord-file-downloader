# discord-file-downloader
Downloads files from discord messages.

## Installation
- `git clone`
- check python installation (>= 3.08)
- install [discord.py](https://discordpy.readthedocs.io/en/stable/intro.html) via `pip` or another tool
- rename `secrets template.json` to `secrets.json` and fill `"discord_client_secret"`
- set up the config file to your needs (`config.json`)

## Directory set-up
```
/[project folder]
  ./config.json
  ./secrets.json
  ./app.py
  ./LocalClient.py
  ./.gitignore
  ``` 
  *the .gitignore file is not required nor used by the app, but you will download it when you clone the repository*
