from enum import Enum, auto
import discord
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
                message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
            return ["I found this message:", "```" + message.author.name + ": " + message.content + "```",
                    "Please select reason for reporting post. Respond using letter choice below:\n"
                    "A. Pro-ED Content\n"
                    "B. ED-Related Concern for User"]
        
        if self.state == State.MESSAGE_IDENTIFIED:
            content = message.content.lower()
            if content == "a":
                self.state = State.PRO_ED
                return ["Please make your best attempt to identify the type of pro-ED content in this message. Respond using letter choice below:\n"
                        "A. Content encourages user(s) to develop an eating disorder\n"
                        "B. Content describes a crash diet or extreme exercise challenge\n"
                        "C. Content lays out step-by-step instructions on how to effectively starve or purge"]
            elif content == "b":
                self.state = State.ED_CONCERN
                return ["Would you like us to look at this post and offer support to this user? Your name will be kept confidential. Respond using letter choice below:\n"
                        "A. Yes\n",
                        "B. No"]

        if self.state == State.PRO_ED:
            content = message.content.lower()
            if content == "a":
                self.state = State.PRO_ED_A
                return ["If possible, please try to identify the way this piece of content encourages user(s) to develop an editing disorder.\n"
                        "Please respond with the letter choice corresponding to the reported message content.\n"
                        "A. \"Meanspiration\" or content that attacks, bullies, or makes fun of user(s)\n"
                        "B. Content that praises eating disorders as a lifestyle choice\n"
                        "C. Content that derides the notion of ED-recovery"]
            elif content == "b" or content == "c":
                self.state = State.REPORT_COMPLETE
                return ["Thank you for submitting your report. We will remove the content after corroborating that content is violative of ED-related platform policies."]

        if self.state == State.PRO_ED_A:
            content = message.content.lower()
            if content == "a" or content == "b" or content == "c":
                self.state = State.REPORT_COMPLETE
                return ["Thank you for submitting your report. We will remove the content after corroborating that content is violative of ED-related platform policies."]

        if self.state == State.ED_CONCERN:
            content = message.content.lower()
            if content == "a":
                self.state = State.REPORT_COMPLETE
                return ["Thank you for submitting your report. We will reach out to this individual with contact information for the National Eating Disorder Information Centre (NEDIC). If this person is in immediate danger please do not hesitate to contact local emergency services."]
            elif content == "b":
                self.state = State.REPORT_COMPLETE
        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
    


    

