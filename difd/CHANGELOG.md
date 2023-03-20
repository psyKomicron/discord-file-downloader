# **Change log**
# 0.0.4
## Changes
- Added option to download the latest release from GitHub when using `install.py`.
- Added `try/catch` when syncing commands.
    - If `exit_on_error` is set to `True` the application will exit if it failed to sync.
- Only using specific guild when `DEBUG` is set to `True`. 
- Updated default download directory to `./downloads` (from `./difd/downloads`).
- Added `allowed_users` to config and but not configuration steps. The user will need to manually set this field.

## Fixes
- Fixed error while syncing methods. The bot was trying to sync commands in a guild it did not have access to.

## Bugs
- If the `./downloads/` directory is not created, the download command will fail (`batcher.download` doesn't create the dir).

## Todo
- [X] Handle messages.
- [X] Download images.
- [ ] Easier and prettier config.
- [ ] More robust config and token handling. *still not robust enough*
- [ ] Handle exceptions and forbidden channels.
- [X] Config needs to configure `allowed_users`.
- [ ] Try to run python script as an executable, so that users don't have to use a terminal to start it.


# 0.0.3
## Changes
- Refactored `config.py` to move `Config` class to `autoconfig.py` (fixes recursive dependency between `translations.py` and `config.py`). Thus refactored files dependent upon `config.py`
- Created `install.py` (script) to download the app from GitHub using `git` and download python dependencies.
- Updated `README.md`
- Added `DEPENDENCIES` in `config.py` for installer.

## Fixes
- The bot now fetches the right number of files, until the end of the channel if necessary.

## Bugs
- If the `./downloads/` directory is not created, the download command will fail (`batcher.download` doesn't create the dir).
- Config will fail often.

## Todo
- [X] Handle messages.
- [X] Download images.
- [ ] Easier and prettier config.
- [ ] More robust config and token handling. *still not robust enough*
- [ ] Handle exceptions and forbidden channels.
- [ ] Config needs to configure `allowed_users`.

# 0.0.2
## Changes
- Added batch download, to more efficiently download a large number of files.
- Added more config constants.
- `app.py` has been moved to `./difd` and imports have been refactored to account for that.
- More structural changes not listed.

## Fixes
- Potential timeout error when downloading big files (should not have happened since discord only allows small files).
- Actually choosing files when downloading resources (using `config.VALID_FILE_RE` and `config.RESOURCE_RE`).
- Fixed download command not downloading the wanted number of messages (even if there was enough files in one fetch).

## Bugs
- The bot doesn't actually download the wanted number of files, neither does it parse the wanted number of files. It actually only fetches `config.json[max_fetch_files]` and then tries to find valid files or resources in those messages.
- If the `./downloads/` directory is not created, the download command will fail (`batcher.download` doesn't create the dir).
- Config will fail often.

## Todo
- [X] Handle messages.
- [X] Download images.
- [ ] Easier and prettier config.
- [ ] More robust config and token handling. *still not robust enough*
- [ ] Handle exceptions and forbidden channels.
- [ ] Config needs to configure `allowed_users`.


# 0.0.1 
## Changes
- Removed LocalClient, main will handle all logic.
- Created auto config to guide the user through the configuration process.
- Streamlined (a bit) startup process.

## Fixes
None

## Bugs
- Application does not actually handle messages.
- No downloads.
- Config will fail often.

## Todo
- [ ] Handle messages.
- [ ] Download images.
- [ ] Easier and prettier config.
- [ ] More robust config and token handling.
