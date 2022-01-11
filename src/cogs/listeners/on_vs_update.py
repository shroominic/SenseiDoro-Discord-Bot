
from discord.ext.commands import Cog
import asyncio


class OnVSUpdate(Cog, name='OnVSUpdate module'):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        This function gets called, when something changes in voice channels.
        """
        if before.channel is not None:
            if before.channel.name == "START SESSION":
                # TODO: Fix this workaround
                return
        if after.channel is not None:
            if after.channel.name == "START SESSION":
                session_name = after.channel.category.name
                # searches for the addressed session
                for sees in self.bot.sessions:
                    if sees.name == session_name:
                        asyncio.create_task(sees.start_session(member))
