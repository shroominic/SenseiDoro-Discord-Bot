from discord.ext.commands import Cog
import asyncio
import json

from src.session import Session, env_manager
from dojo import Dojo


class OnReady(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        """
        When the bot has fully started,
        this function will get called.
        """
        for guild in self.bot.guilds:
            dojo = Dojo(guild=guild, bot=self.bot)
            self.bot.dojos[guild.id] = dojo
        # serialize old session instances
        for guild in self.bot.guilds:
            for category in guild.categories:
                if "🍅" in category.name:
                    asyncio.create_task(self.serialize(category))

        # print all connected guilds
        all_guilds = [guild.name for guild in self.bot.guilds]
        print(f'{self.bot.user} is connected to the following guilds: \n{all_guilds}\n')
        print('READY')

    # helper function to fetch old sessions
    async def serialize(self, category):
        """
        Searches for all pomodoro sessions on the server
        to reinitialize lost instances during a restart.
        :param category: category of session to serialize
        """
        # get dojo reference
        dojo = self.bot.dojos[category.guild.id]
        # find message with session config
        for tc in category.text_channels:
            if tc is not None:
                if tc.name == Session.config_label:
                    async for msg in tc.history():
                        if msg.author == self.bot.user and msg.content.startswith('Session config:'):
                            # parse string representation of json
                            config_json = str(msg.content)[15::]
                            config = json.loads(config_json)
                            # create session instance from json
                            session_instance = Session(
                                dojo=dojo,
                                category=category,
                                work_time=config["work_time"],
                                break_time=config["pause_time"],
                                repetitions=config["number_sessions"],
                                session_name=config["name"])
                            dojo.sessions[category.id] = session_instance
                            await env_manager.create_from_old_environment(session_instance)
