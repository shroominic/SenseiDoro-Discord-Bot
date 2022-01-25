import asyncio

from discord.utils import get


class Dojo:
    def __init__(self, guild, bot, session_limit=2):
        self.guild = guild
        self.bot = bot
        self.session_limit = session_limit
        self.sessions = {}
        self.dojo_manager_role = None
        # async init
        asyncio.create_task(self.init_async())

    async def init_async(self):
        if not get(self.guild.roles, name="Dojo Manager"):
            self.dojo_manager_role = await self.guild.create_role(name="Dojo Manager")
        else:
            self.dojo_manager_role = get(self.guild.roles, name="Dojo Manager")
