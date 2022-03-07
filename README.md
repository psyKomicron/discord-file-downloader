# discord-file-downloader
Downloads files from discord messages.

## Installation
- `git clone https://github.com/psyKomicron/discord-file-downloader.git`
- check python installation (>= 3.08):
 - `python3 --version`
- install [discord.py](https://discordpy.readthedocs.io/en/stable/intro.html) via `pip` or another tool
- install [requests](https://docs.python-requests.org/en/latest/user/install/#install) via `pip` or another tool **don't forget to use python3 to install**
- rename `secrets template.json` to `secrets.json` and fill `"discord_client_secret"`
- set up the config file to your needs (`config.json`). [Configuration](## Configuration)

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

## Configuration
The configuration for the app is handled by the `config.json` file.
### `max_fetch_files`:
Maximum number of files to fetch when looking to download files. The app fetches `max_fetch_files` when the `!get-images` command is received, then parse those messages to search for files.

For example if you set it to 100, the app will fetch the last 100 messages in the channel and search if any of those 100 messages have files. 

**This does not mean that it will download 100 files. some messages may not have files attached, some may have more than 1 file attached**

### `show_unhandled_messages`
Prints a message in the console everytime the app receives a message.

### `exit_on_error`
When downloading files errors/exceptions may be raised. Set this property to `True` if you want the app to exit when this happens, set it to `False` to just keep the application running

### `download_folder_path`
The path, absolute or relative, to the folder where you want the downloaded files to go. If the folder does not exists, it will be created.

### `valid_files`
Regular expression that every file must match. *Note : the regular expression will be tested on the download url, not on the file name itself.*

### `show_skips`
Show the files (download url) that do not match `valid_files`.
- `True` if you want to show those files.
- `False` if you want to ignore those files.

### `exit_after_command`
- `True` the application once the command `!get-images` has completed will exit.
- `False` the application once the command `!get-images` has completed will keep running.
