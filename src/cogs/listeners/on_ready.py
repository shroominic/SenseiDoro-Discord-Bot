from discord.ext.commands import Cog
import asyncio
import json

from src.models.session import Session


class OnReady(Cog, name='OnReady module'):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        """
        When the bot has fully started,
        this function will get called.
        """
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
        """
        # find message with session config
        for tc in category.text_channels:
            if tc is not None:
                if "session_chat" in tc.name:
                    async for msg in tc.history(limit=200):
                        if msg.author == self.bot.user and msg.content.startswith('Session config:'):
                            # parse string representation of json
                            config_json = str(msg.content)[15::]
                            config = json.loads(config_json)
                            # create session instance from json
                            session = Session(
                                msg.guild,
                                category,
                                config["work_time"],
                                config["pause_time"],
                                config["number_sessions"])
                            self.bot.sessions.append(session)
                            await session.setup_old_environment()