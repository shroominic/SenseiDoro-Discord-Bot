from session import Session
import discord
import asyncio
import json


# Bot Client Class
class PomoDojoClient(discord.Client):
    def __init__(self, *args, **options):
        super(PomoDojoClient, self).__init__(*args, **options)
        # stores all open sessions
        self.sessions: [Session] = []

    # when bot starts up
    async def on_ready(self):
        # serialize old session instances
        for guild in self.guilds:
            for category in guild.categories:
                if "🍅" in category.name:
                    asyncio.create_task(self.serialize(category))
        # print all connected guilds
        all_guilds = [guild.name for guild in self.guilds]
        print(f'{self.user} is connected to the following guilds: \n{all_guilds}\n')
        print('READY')

    # when a new message shows up
    async def on_message(self, message):
        if message.author == self.user:
            # ignores messages from itself
            return

        # init a pomodoro session
        if message.content == "/init":
            session = Session(message.guild)
            # checks if session already exists
            for sees in self.sessions:
                if sees.name == session.name:
                    asyncio.create_task(message.channel.send('Session already exists!'))
                    del session
                    return
            self.sessions.append(session)
            # initializes the session category and channels
            asyncio.create_task(session.create_environment())

        # cleanup all previous sessions
        if message.content == "/cleanup":
            asyncio.create_task(message.channel.send("Yeah mom, I'll cleanup my room very soon!"))
            # deletes active sessions
            for sees in self.sessions:
                asyncio.create_task(sees.dispose())

        # delete all messages inside message.channel
        if message.content == "/delete":
            await message.channel.send("I'll delete all messages in this channel!")
            async for msg in message.channel.history(limit=100):
                asyncio.create_task(msg.delete())

    # when something changes in voice channels
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None:
            if before.channel.name == "START SESSION":
                # TODO: Fix this workaround
                return
        if after.channel is not None:
            if after.channel.name == "START SESSION":
                session_name = after.channel.category.name
                # searches for the addressed session
                for sees in self.sessions:
                    if sees.name == session_name:
                        asyncio.create_task(sees.start_session(member))

    # helper function to fetch old sessions
    async def serialize(self, category):
        # find message with session config
        for tc in category.text_channels:
            if tc is not None:
                if "session_chat" in tc.name:
                    async for msg in tc.history(limit=200):
                        if msg.author == self.user and msg.content.startswith('Session config:'):
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
                            self.sessions.append(session)
                            await session.setup_old_environment()





