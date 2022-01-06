# Application Main

from pomodojo_client import PomoDojoClient
from dotenv import load_dotenv
import discord
import os

# load token from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# client can see all users
intents = discord.Intents.default()
intents.members = True


# init and start client
if __name__ == '__main__':
    client = PomoDojoClient(intents=intents)
    client.run(TOKEN)

