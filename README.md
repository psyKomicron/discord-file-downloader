# FR
# discord-file-downloader
Telecharge des fichiers de messages Discord.
## How-to
- Pour télécharger des fichiers, depuis Discord tapez ` !get-images` dans le salon textuel duquel vous voulez télécharger des fichiers. Une fois le message envoyé, l’application téléchargera les fichiers en vous informant du progrès via la console.
- Pour lancer l’application, assurez-vous que vous avez suivi les [étapes d’installation](#Installation). Ouvrez un terminal puis naviguez si besoin est à la racine de l’application. Tapez ensuite `python3 app.py` pour démarrer l’application, vous devriez avoir le message suivant dans la console
  
  ```
  bot > logged in as [bot name], waiting for command
  ```

## Installation
- `git clone https://github.com/psyKomicron/discord-file-downloader.git`
- Vérifiez que python version 3 ou supérieur est bien installé. `python3 --version`
- Installez [discord.py](https://discordpy.readthedocs.io/en/stable/intro.html) via `pip` ou un autre outil.
- Installez [requests](https://docs.python-requests.org/en/latest/user/install/#install) via `pip` ou un autre outil. **ne pas oubliez d'utiliser python3 pour installer (python3 au lieu de python ou py)**
- Renommez `secrets template.json` en `secrets.json` remplissez le champ `"discord_client_secret"`.
- Mettez en place le fichier de configuration selon vos besoins. (`config.json`).Tutoriel -> [Configuration](#Configuration).

## Paramétrage de répertoire
```
discord-file-downloader/
├── config.json
├── secrets.json
├── app.py
├── LocalClient.py
└── .gitignore
  ``` 
  *le fichier `.gitignore` n'est pas nécessaire au fonctionnement de l'application.*

## Configuration
La configuration de l’application est gérée par le fichier `config.json`.
### `max_fetch_files`:
Nombre maximum de messages a collecter lors de la recherche de fichiers. L’application requête Discord pour `max_fetch_files` messages puis cherche parmi ces messages ceux qui ont des fichiers joints valides.

Par exemple, si `max_fetch_files` est paramétré a 100 l’application collectera les 100 derniers messages du salon dans lequel la commande a été envoyée puis cherchera parmi ces 100 messages ceux qui ont des fichiers valides pour ensuite les télécharger.

**Cela ne veut pas dire que l’application va télécharger 100 fichiers. Certains messages n’auront pas de fichiers valides, certains en auront plus d’un**

### `show_unhandled_messages`
Affiche un message dans la console chaque fois qu’un message est reçu par l’application.

### `exit_on_error`
Lors de la collection des messages et du téléchargement des fichiers par l’application, une erreur peut se produire (fichier corrompu, lien de téléchargement cassé…).
- `True` l’application cessera son exécution lors d’une erreur.
- `False` l’application continuera de tourner.

### `download_folder_path`
Le chemin, absolu ou relatif, vers le répertoire ou les fichiers téléchargés seront sauvegardés. Si le répertoire n’existe pas, l’application le créera.

### `valid_files`
Expression régulière que chaque fichier doit vérifier pour être téléchargé.

*Note : l’expression régulière est appliquée au lien de téléchargement et non au nom du fichier seulement.*

### `show_skips`
Affiche dans la console les fichiers (lien du fichier) qui ne vérifient pas `valid_files`.
- `True` pour afficher ces fichiers.
- `False` pour les ignorer.

### `exit_after_command`
- `True` l'application se fermera une fois les téléchargements effectués.
- `False` l'application restera ouverte une fois les téléchargements effectués.


# EN
# discord-file-downloader
Downloads files from discord messages. 
## How-to
- To download files, type `!get-images` in the Discord channel where you want to download images, and wait for the app to download them (application progress is show in the console).
- To start the application make sure you followed [installation steps](#Installation), then open a terminal in the application folder. Type `python3 app.py` to start the app, you should get :
  
  ```
  bot > logged in as [bot name], waiting for command
  ```

## Installation
- `git clone https://github.com/psyKomicron/discord-file-downloader.git`
- check python installation (>= 3.08):
 - `python3 --version`
- install [discord.py](https://discordpy.readthedocs.io/en/stable/intro.html) via `pip` or another tool
- install [requests](https://docs.python-requests.org/en/latest/user/install/#install) via `pip` or another tool **don't forget to use python3 to install**
- rename `secrets template.json` to `secrets.json` and fill `"discord_client_secret"`
- set up the config file to your needs (`config.json`). [Configuration](#Configuration)

## Directory set-up
```
discord-file-downloader/
├── config.json
├── secrets.json
├── app.py
├── LocalClient.py
└── .gitignore
  ``` 
  *the `.gitignore` file is not required nor used by the app, but you will download it when you clone the repository*

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
