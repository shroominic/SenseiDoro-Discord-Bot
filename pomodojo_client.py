from session import Session
import discord
import asyncio


# Bot Client Class
class PomoDojoClient(discord.Client):
    def __init__(self, *args, **options):
        super(PomoDojoClient, self).__init__(*args, **options)
        # stores all open sessions
        self.sessions: [Session] = []

    # when bot starts up
    async def on_ready(self):
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
            asyncio.create_task(self.cleanup(message.guild))

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

    async def cleanup(self, guild):
        for sees in self.sessions:
            asyncio.create_task(sees.dispose())
        # deletes sessions from previous times
        for category in guild.categories:
            if "🍅" in category.name:
                for vc in category.voice_channels:
                    channel_id = vc.id
                    asyncio.create_task(self.get_channel(channel_id).delete())
                for tc in category.text_channels:
                    channel_id = tc.id
                    asyncio.create_task(self.get_channel(channel_id).delete())
                asyncio.create_task(category.delete())