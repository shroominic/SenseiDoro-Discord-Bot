# Discord Pomodoro Bot

import os
import discord
from dotenv import load_dotenv

from session import Session

# load token from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# client can see all users
intents = discord.Intents.default()
intents.members = True


class PomoDojoClient(discord.Client):
    def __init__(self, *args, **options):
        super(PomoDojoClient, self).__init__(*args, **options)
        self.sessions: [Session] = []

    async def on_ready(self):
        # print all connected guilds
        all_guilds = [guild.name for guild in self.guilds]
        print(f'{self.user} is connected to the following guilds: \n{all_guilds}\n')

        print('READY')

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
                    await message.channel.send('Session already exists!')
                    return
            # initializes the session category and channels
            await session.create_environment()
            self.sessions.append(session)

        # cleanup all previous sessions
        if message.content == "/cleanup":
            await message.channel.send("Yeah mom, I'll cleanup my room very soon!")
            for category in message.guild.categories:
                if "🍅" in category.name:
                    for vc in category.voice_channels:
                        await vc.delete()
                    for tc in category.text_channels:
                        await tc.delete()
                    await category.delete()

        # delete all messages inside message.channel
        if message.content == "/delete":
            await message.channel.send("I'll delete all messages in this channel!")
            async for msg in message.channel.history(limit=200):
                await msg.delete()

    async def on_voice_state_update(self, member, before, after):
        if after.channel.name == "START SESSION":
            session_name = after.channel.category.name
            # searches for the addressed session
            for sees in self.sessions:
                if sees.name == session_name:
                    await sees.start_session(member)


if __name__ == '__main__':
    # init and start client
    client = PomoDojoClient(intents=intents)
    client.run(TOKEN)

