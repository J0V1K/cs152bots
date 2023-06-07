from enum import Enum, auto
import discord
from discord.ui import Button, View
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    REPORT_COMPLETE = auto()
    PRO_ED = auto()
    PRO_ED_A = auto()
    ED_CONCERN = auto()
    SUBMIT_REPORT = auto()

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.message = None
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''

        if message.content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        
        if self.state == State.REPORT_START:
            reply = "Thank you for starting the reporting process. "
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
            guild = self.client.get_guild(int(m.group(1)))
            if not guild:
                return ["I cannot accept reports of messages from guilds that I'm not in. Please have the guild owner add me to the guild and try again."]
            channel = guild.get_channel(int(m.group(2)))
            if not channel:
                return ["It seems this channel was deleted or never existed. Please try again or say `cancel` to cancel."]
            try:
                self.message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
            return ["I found this message:", "```" + self.message.author.name + ": " + self.message.content + "```",
                    "Please select reason for reporting post. Respond using letter choice below:\n"
                    "A. Pro-ED Content\n"
                    "B. ED-Related Concern for User"]
        a_responses = ["a", "a."]
        b_responses = ["b", "b."]
        c_responses = ["c", "c."]
        if self.state == State.MESSAGE_IDENTIFIED:
            content = message.content.lower()
            if content in a_responses:
                self.state = State.PRO_ED
                return ["Please make your best attempt to identify the type of pro-ED content in this message. Respond using letter choice below:\n"
                        "A. Content encourages user(s) to develop an eating disorder\n"
                        "B. Content describes a crash diet or extreme exercise challenge\n"
                        "C. Content lays out step-by-step instructions on how to effectively starve or purge"]
            elif content in b_responses:
                self.state = State.ED_CONCERN
                return ["Would you like us to look at this post and offer support to this user? Your name will be kept confidential. Respond using letter choice below:\n"
                        "A. Yes\n"
                        "B. No"]

        if self.state == State.PRO_ED:
            content = message.content.lower()
            if content in a_responses:
                self.state = State.PRO_ED_A
                return ["If possible, please try to identify the way this piece of content encourages user(s) to develop an editing disorder.\n"
                        "Please respond with the letter choice corresponding to the reported message content.\n"
                        "A. \"Meanspiration\" or content that attacks, bullies, or makes fun of user(s)\n"
                        "B. Content that praises eating disorders as a lifestyle choice\n"
                        "C. Content that derides the notion of ED-recovery"]
            elif content in b_responses + c_responses:
                if content in b_responses:
                    flag = "crash"
                else: 
                    flag = "starve"
                author_id = self.message.author.id
                user = await self.client.fetch_user(author_id)
                dm_channel = user.dm_channel
                if dm_channel == None:
                    dm_channel = await user.create_dm()
                embed = discord.Embed(title=f'sent problematic message:\n "{self.message.content}"', description="Use the button below to flag the message if appropriate.")
                embed.color = discord.Color.orange()
                embed.set_author(name=message.author.name + "#" + self.message.author.discriminator, icon_url=self.message.author.avatar.url)
                embed.add_field(name="Category: " + flag, value=f'Manually Reported by:\n "{message.author.name}#{message.author.discriminator}"', inline="False")
                mod_channel = discord.utils.get(self.client.get_all_channels(), name="group-23-mod")
                #
                footer = "Message ID:" + str(self.message.id) + ":" + str(author_id)
                embed.set_footer(text=footer)
                button = Button(label="Flag Message", style=discord.ButtonStyle.danger, emoji="❌")
                async def button_callback(interaction):
                    await interaction.response.defer(ephemeral = True, thinking = True)
                    footer_content = interaction.message.embeds[0].footer.text.split(':')
                    flagged_id = int(footer_content[1])
                    regular_channel = discord.utils.get(self.message.guild.channels, name='group-23')
                    flagged_message = await regular_channel.fetch_message(flagged_id)
                    await flagged_message.add_reaction('❌')

                    author_id = footer_content[2]
                    user = await self.client.fetch_user(author_id)
                    dm_channel = user.dm_channel
                    if dm_channel == None:
                        dm_channel = await user.create_dm()
                    await dm_channel.send("Your post has been flagged for ED content. Please be mindful about the impact of your words both on yourself and others.")
                    await interaction.followup.send(content="Message Flagged.")
                    return
                button.callback = button_callback
                view= View()
                view.add_item(button)
                await mod_channel.send(embed=embed, view=view)
                self.state = State.REPORT_COMPLETE
                return ["Thank you for submitting your report. We will remove the content after corroborating that content is violative of ED-related platform policies."]

        if self.state == State.PRO_ED_A:
            content = message.content.lower()
            if content in a_responses + b_responses + c_responses:
                if content in a_responses:
                    flag = "meanspiration"
                elif content in b_responses: 
                    flag = "praises"
                else: 
                    flag = "derides"
                author_id = self.message.author.id
                user = await self.client.fetch_user(author_id)
                dm_channel = user.dm_channel
                if dm_channel == None:
                    dm_channel = await user.create_dm()
                embed = discord.Embed(title=f'sent problematic message:\n "{self.message.content}"', description="Use the button below to flag the message if appropriate.")
                embed.color = discord.Color.orange()
                embed.set_author(name=message.author.name + "#" + self.message.author.discriminator, icon_url=self.message.author.avatar.url)
                embed.add_field(name="Category: " + flag, value=f'Manually Reported by:\n "{message.author.name}#{message.author.discriminator}"', inline="False")
                mod_channel = discord.utils.get(self.client.get_all_channels(), name="group-23-mod")
                #
                footer = "Message ID:" + str(self.message.id) + ":" + str(author_id)
                embed.set_footer(text=footer)
                button = Button(label="Flag Message", style=discord.ButtonStyle.danger, emoji="❌")
                async def button_callback(interaction):
                    await interaction.response.defer(ephemeral = True, thinking = True)
                    footer_content = interaction.message.embeds[0].footer.text.split(':')
                    flagged_id = int(footer_content[1])
                    regular_channel = discord.utils.get(self.message.guild.channels, name='group-23')
                    flagged_message = await regular_channel.fetch_message(flagged_id)
                    await flagged_message.add_reaction('❌')

                    author_id = footer_content[2]
                    user = await self.client.fetch_user(author_id)
                    dm_channel = user.dm_channel
                    if dm_channel == None:
                        dm_channel = await user.create_dm()
                    await dm_channel.send("Your post has been flagged for ED content. Please be mindful about the impact of your words both on yourself and others.")
                    await interaction.followup.send(content="Message Flagged.")
                    return
                button.callback = button_callback
                view= View()
                view.add_item(button)
                await mod_channel.send(embed=embed, view=view)
                self.state = State.REPORT_COMPLETE
                return ["Thank you for submitting your report. We will remove the content after corroborating that content is violative of ED-related platform policies."]

        if self.state == State.ED_CONCERN:
            content = message.content.lower()
            if content in a_responses:
                author_id = message.author.id
                user = await self.client.fetch_user(author_id)
                dm_channel = user.dm_channel
                if dm_channel == None:
                    dm_channel = await user.create_dm()
                embed = discord.Embed(title=f'Are you doing okay?', description="We are reaching because we want to support you. Someone is concerned that you might be experiencing harmful habits. Please don't hesitate to call 1-866-NEDIC-20 to talk to someone who can understand and help you.")
                embed.color = discord.Color.yellow()
                embed.add_field(name="Resources:", value="[Click here to contact NEDIC](https://nedic.ca/contact/)", inline="False")
                await dm_channel.send(embed=embed)
                self.state = State.REPORT_COMPLETE
                return ["Thank you for submitting your report. We will reach out to this individual with contact information for the National Eating Disorder Information Centre (NEDIC). If this person is in immediate danger please do not hesitate to contact local emergency services."]
            elif content in b_responses:
                self.state = State.REPORT_COMPLETE
                return ["You have decided not to file the report on this message. Please feel free to report a genuine concern at any time."]
        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
    


    

