from src.models.session import Session
from discord.ext import commands
import asyncio


# Bot Client Class
class PomoDojoClient(commands.Bot):
    def __init__(self, *args, **options):
        super(PomoDojoClient, self).__init__(*args, **options)
        # stores all open sessions
        self.sessions: [Session] = []

    # when a new message shows up
    async def on_message(self, message):
        if message.author == self.user:
            # ignores messages from itself
            return

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
