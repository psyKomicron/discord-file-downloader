import discord
import discord.app_commands
import re
import requests
import io
import translations
from logging import Logger
from typing import *
from discord import Client, Intents, Interaction, HTTPException, Forbidden
from discord.app_commands import CommandTree
from config import RESOURCE_RE, VALID_FILES_RE, DEBUG
from autoconfig import Config
from batcher import Batcher
if DEBUG:
    from console import shortPrint 


class CommandHandler(Client):
    guild: int
    commandTree: CommandTree
    config: Config
    logger: Logger
    batcher: Batcher = Batcher(10, 1000)

    def __init__(self, config: Config, intents: Intents, logger: Logger, **options: Any) -> None:
        super().__init__(intents=intents, **options)
        # If we are running in debug mode, only use the bot in La-Famille.
        self.guild = discord.Object(id=289090423031463936) if DEBUG else None
        self.config = config
        self.logger = logger
        self.batcher.downloadFolderPath = config.download_folder_path

        self.commandTree = CommandTree(self)        
        @self.commandTree.command(name="download_command_name", description="download_command_description", guild=self.guild)
        async def download(interaction: Interaction, count: int):
            if self._userAllowed(interaction.user):
                try:
                    await self.handleDownload(interaction, count)
                except Exception as ex:
                    self.logger.error(ex)
            else:
                self.logger.debug(f"{interaction.user.name}#{interaction.user.discriminator} not allowed to use download command")

        @self.commandTree.command(name="clean_command_name", description="clean_command_description", guild=self.guild)
        async def clean(interaction: Interaction, username:str = None):
            try:
                await self.handleClean(interaction, username)
            except Forbidden:
                await interaction.response.send_message(translations.getString("clean_command_failed_forbidden"), ephemeral=True)
            except HTTPException as ex:
                # TODO: Better logging
                logger.warning("Failed to delete messages")
                logger.error(ex)
    

    async def handleDownload(self, interaction: Interaction, count: int):
        c = 0
        self.logger.info(f"Received {interaction.command.qualified_name} from {interaction.user.name}")
        await interaction.response.defer(thinking=True, ephemeral=True)
        resources = []
        lastFetchedMessage: discord.Message = None
        # First pass to check if we can have enough files with a simple fetch.
        async for message in interaction.channel.history(limit=self.config.max_fetch_size):
            c += 1
            if len(message.attachments) > 0:
                # Get attachements
                for attachement in message.attachments:
                    if VALID_FILES_RE.search(attachement.url):
                        resources.append(attachement.url)
                        self.logger.debug(f"[{count - len(resources)}] Added content from {message.author.name} '{attachement.filename}'")
            else:
                reMatches = RESOURCE_RE.search(message.clean_content)
                if reMatches and len(reMatches.group()) > 0:
                    for match in reMatches.group():
                        if VALID_FILES_RE.search(match):
                            resources.append(match)
                            self.logger.debug(f"[{count - len(resources)}] Added resources from {message.author.name} '{match}'")
            if len(resources) > count:
                self.logger.debug("Found enough files, breaking fetch loop")
                break
            lastFetchedMessage = message
        # If we havent found enough files with a simple fetch, fall back to fetching messages manually and checking for files for every message in the channel.
        if len(resources) < count:
            self.logger.info(f"Fetching more messages to find enough files to satisfy the request")
            while len(resources) < count:
                self.logger.debug(f"Last message: {message.created_at.strftime('%Y-%m-%d %H:%M')} @{message.author.name} {message.content}")
                limit = count - len(resources) if count - len(resources) <= self.config.max_fetch_size else self.config.max_fetch_size 
                fetchedMessages = interaction.channel.history(limit=limit, before=lastFetchedMessage.created_at)
                async for message in fetchedMessages:
                    c += 1
                    if len(message.attachments) > 0:
                        # Get attachements
                        for attachement in message.attachments:
                            if VALID_FILES_RE.search(attachement.url):
                                resources.append(attachement.url)
                                self.logger.debug(f"[{count - len(resources)}] Added content from {message.author.name} '{attachement.filename}'")
                    else:
                        reMatches = RESOURCE_RE.search(message.clean_content)
                        if reMatches and len(reMatches.group()) > 0:
                            for match in reMatches.group():
                                if VALID_FILES_RE.search(match):
                                    resources.append(match)
                                    self.logger.debug(f"[{count - len(resources)}] Added resources from {message.author.name} '{match}'")
                    if len(resources) > count:
                        self.logger.debug("Found enough files, breaking fetch loop")
                        break
                    lastFetchedMessage = message
                else:
                    self.logger.info("Reached end of channel, no more messages available")
                    break
        self.logger.debug(f"Fetched total of {c} messages")
        # TODO: i18n
        if len(resources) > 0:
            try:
                await interaction.followup.send(content=f"Found {len(resources)} files.\nStarting download... 🤔️", ephemeral=True)
            except Exception as ex:
                self.logger.warning("Failed to send user found files number feedback")
                self.logger.error(ex)
        else:
            self.logger.warning("Nothing to download, exiting download command")
            try:
                await interaction.followup.send(content=f"Nothing to download ! 😥️", ephemeral=True)
            except Exception as ex:
                self.logger.warning("Failed to send no file found feedback")
                self.logger.error(ex)
            return
        self.logger.info("Batching files...")
        downloads = await self.batcher.batch(resources)
        try:
            rate = "{:.1f}%".format(self.batcher.successRate * 100)
            await interaction.followup.send(content=f"✅️ ({rate} | {downloads}/{len(resources)})", ephemeral=True)
        except Exception as ex:
            self.logger.error(ex)
            

    async def handleClean(self, interaction: Interaction, username: str = None):
        await interaction.response.pong()
        if username:
            """Deletes messages by username"""
            regEx = re.compile(username)
            count = 0
            async for message in interaction.channel.history(limit=self.config.max_fetch_size):
                if message and message.author and regEx.search(f"{message.author.name}#{message.author.discriminator}"):
                    # not awaiting
                    await message.delete()
                    count += 1
            self.logger.info(f"Deleted {count} messages from {username} (requested by {interaction.user.display_name})")
            interaction.response.send_message(translations.getString("deleted_x_messages").format(count))
    

    async def on_ready(self):
        self.logger.info("Ready, syncing commands and setting translator...")
        await self.commandTree.set_translator(translations.Translator2())
        try:
            commands = await self.commandTree.sync(guild=self.guild)
            if commands:
                self.logger.info("Commands synced and ready")
                s = []
                for command in commands:
                    options = ""
                    for option in command.options:
                        options += option.name
                    s.append(f"{command.name}: {options}")
                self.logger.info("Available commands -> [" + ", ".join(s) + "]")
            else:
                self.logger.info("CommandTree.sync returned None")
        except Exception as ex:
            self.logger.critical("Failed to sync commands.")
            self.logger.error(ex)
            if self.config.exit_on_error:
                exit(-1)


    def _userAllowed(self, user: discord.User) -> bool:
        return f"{user.name}#{user.discriminator}" in self.config.allowed_users