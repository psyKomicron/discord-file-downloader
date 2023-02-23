from logging import Logger
from typing import *
import discord
import discord.app_commands
from discord import Client, Intents, Interaction, HTTPException, Forbidden
from discord.app_commands import CommandTree
import re
import difd.config as config
from difd.config import Config
import difd.translations as translations
import requests
import io


class CommandHandler(Client):
    guild: int
    commandTree: CommandTree
    config: Config
    logger: Logger

    def __init__(self, guild: int, config: Config, intents: Intents, logger: Logger, **options: Any) -> None:
        super().__init__(intents=intents, **options)
        self.guild = guild
        self.config = config
        self.logger = logger

        self.commandTree = CommandTree(self)
        
        @self.commandTree.command(name="download_command_name", description="download_command_description", guild=discord.Object(id=guild))
        async def download(interaction: Interaction, count: int):
            await self.handleDownload(interaction)

        @self.commandTree.command(name="boobies", description="(.)Y(.)", guild=discord.Object(id=guild))
        async def boobies(interaction: Interaction):
            # Bob :)
            get = requests.get("https://cdn.7tv.app/emote/60aecad55174a619dbb774f2/4x.webp")
            interaction.command_failed = True
            if get.ok:
                file = get.content
                try:
                    await interaction.channel.send(content="Bob", file=io.BytesIO(file))
                    interaction.command_failed = False
                except Exception as ex:
                    self.logger.warning(f"Failed to send https://cdn.7tv.app/emote/60aecad55174a619dbb774f2/4x.webp to discord.\n{ex}")
            
            if interaction.command_failed:
                await interaction.response.send_message("bob")

        @self.commandTree.command(name="clean_command_name", description="clean_command_description", guild=discord.Object(id=guild))
        async def clean(interaction: Interaction, username:str = None):
            try:
                await self.handleClean(interaction, username)
            except Forbidden:
                await interaction.response.send_message(translations.getString("clean_command_failed_forbidden"), ephemeral=True)
                pass
            except HTTPException as ex:
                # TODO: Better login
                logger.warning("Failed to delete messages")
                pass
    

    async def handleDownload(self, interaction: Interaction):
        self.logger.info(f"Received {interaction.command.qualified_name} from {interaction.user.name}")
        await interaction.response.send_message(
            f"Downloading: {self.config.max_fetch_size} in {interaction.channel.name}", 
            ephemeral=True
        )
        self.logger.info(f"Command args: {interaction.data}")

        refex = config.RESOURCE_REGEX
        resources = []
        async for message in interaction.channel.history(limit=self.config.max_fetch_size):
            if len(message.attachments):
                # Get attachements
                for attachement in message.attachments:
                    resources.append(attachement.url)
            elif refex.search(message.clean_content):
                resources.append(message.clean_content)

        interaction.response.send_message(f"Found {len(resources)}")


    async def handleClean(self, interaction: Interaction, username: str = None):
        await interaction.response.pong()
        if username:
            """Deletes messages by username"""
            regEx = re.compile(username)
            async for message in interaction.channel.history(limit=self.config.max_fetch_size):
                if message and message.author and regEx.search(f"{message.author.name}#{message.author.discriminator}"):
                    message.delete(delay=30)
                    pass
        pass
    

    async def on_ready(self):
        self.logger.info("Ready, syncing commands and setting translator...")
        await self.commandTree.set_translator(translations.Translator2())

        commands = await self.commandTree.sync(guild=discord.Object(id=self.guild))
        if commands:
            self.logger.info("Commands synced and ready.")
            for command in commands:
                options = ""
                for option in command.options:
                    options += option.name
                self.logger.info(f"\t- {command.name}({options})")
        else:
            self.logger.info("CommandTree.sync returned None")
