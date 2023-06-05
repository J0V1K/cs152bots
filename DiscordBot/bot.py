# bot.py
import discord
from discord.ext import commands, tasks
import os
import json
import logging
import re
import requests
from report import Report
import pdb

from gpt import classify

# Set up logging to the console
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# There should be a file called 'tokens.json' inside the same folder as this file
token_path = 'tokens.json'
if not os.path.isfile(token_path):
    raise Exception(f"{token_path} not found!")
with open(token_path) as f:
    # If you get an error here, it means your token is formatted incorrectly. Did you put it in quotes?
    tokens = json.load(f)
    discord_token = tokens['discord']


class ModBot(discord.Client):
    def __init__(self): 
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='.', intents=intents)
        self.group_num = None
        self.mod_channels = {} # Map from guild to the mod channel id for that guild
        self.reports = {} # Map from user IDs to the state of their report

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord! It is these guilds:')
        for guild in self.guilds:
            print(f' - {guild.name}')
        print('Press Ctrl-C to quit.')

        # Parse the group number out of the bot's name
        match = re.search('[gG]roup (\d+) [bB]ot', self.user.name)
        if match:
            self.group_num = match.group(1)
        else:
            raise Exception("Group number not found in bot's name. Name format should be \"Group # Bot\".")

        # Find the mod channel in each guild that this bot should report to
        for guild in self.guilds:
            for channel in guild.text_channels:
                if channel.name == f'group-{self.group_num}-mod':
                    self.mod_channels[guild.id] = channel

    
    async def on_raw_reaction_add(self, payload):
        '''
        Added by Javo: Checks continously for any new reactions. If reaction is on a specific type of message, emoji reaction will be made by the bot.
        '''

        mod_channel = self.get_channel(payload.channel_id)
        message = await mod_channel.fetch_message(payload.message_id)
        content = message.content.split(':')
        # checks for react to this message with an x
        if content[0] == "React to this message with an ❌ to flag the message publically. Message ID":
            await message.channel.send("Reaction recognized.")
            # flags the appropriate post in the channel with an emoji 
            flagged_id = int(content[1])
            regular_channel = discord.utils.get(message.guild.channels, name='group-23')
            flagged_message = await regular_channel.fetch_message(flagged_id)
            await flagged_message.add_reaction('❌')

    async def on_message(self, message):
        '''
        This function is called whenever a message is sent in a channel that the bot can see (including DMs). 
        Currently the bot is configured to only handle messages that are sent over DMs or in your group's "group-#" channel. 
        '''
        # Ignore messages from the bot 
        if message.author.id == self.user.id:
            return

        # Check if this message was sent in a server ("guild") or if it's a DM
        if message.guild:
            await self.handle_channel_message(message)
        else:
            await self.handle_dm(message)

    async def handle_dm(self, message):
        # Handle a help message
        if message.content == Report.HELP_KEYWORD:
            reply =  "Use the `report` command to begin the reporting process.\n"
            reply += "Use the `cancel` command to cancel the report process.\n"
            await message.channel.send(reply)
            return

        author_id = message.author.id
        responses = []

        # Only respond to messages if they're part of a reporting flow
        if author_id not in self.reports and not message.content.startswith(Report.START_KEYWORD):
            return

        # If we don't currently have an active report for this user, add one
        if author_id not in self.reports:
            self.reports[author_id] = Report(self)

        # Let the report class handle this message; forward all the messages it returns to uss
        responses = await self.reports[author_id].handle_message(message)
        for r in responses:
            await message.channel.send(r)

        # If the report is complete or cancelled, remove it from our map
        if self.reports[author_id].report_complete():
            self.reports.pop(author_id)

    async def handle_channel_message(self, message):
        # Only handle messages sent in the "group-#" channel
        if not message.channel.name == f'group-{self.group_num}':
            return

        # Forward the message to the mod channel
        mod_channel = self.mod_channels[message.guild.id]
        generated = self.eval_text(message.content)
        generated_split = str(generated).split(":")
        generated_flag = generated_split[0]

        # Forward message to the moderator channel only if it is problematic
        if generated_flag != "normal":
            # Message is brought up to the mods. Reaction will trigger on_raw_reaction_add
            await mod_channel.send(f'User: {message.author.name}\nsent problematic message:\n "{message.content}"')
            await mod_channel.send(self.code_format(generated))
            await mod_channel.send("React to this message with an ❌ to flag the message publically. Message ID:" + str(message.id))

    
    def eval_text(self, message):
        ''''
        Classifies text through gpt-4 using our training data.
        '''
        return classify(message)

    
    def code_format(self, text):
        '''
        Generated text is split into the flag and the description.
        '''
        text = str(text).split(":")
        generated_flag = text[0]
        generated_text = text[1]
        return "Flagged as '" + generated_flag + "'\n" + generated_text[1:]

        



client = ModBot()
client.run(discord_token)