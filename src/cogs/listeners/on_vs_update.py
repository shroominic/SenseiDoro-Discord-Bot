
from discord.ext.commands import Cog
import asyncio

from session.env_manager import SessionEnvironment
from src.session import Session, tools


class OnVSUpdate(Cog, name='OnVSUpdate module'):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_voice_state_update(self, _, before, after):
        """ This function gets called, when something changes in voice channels. """
        if after.channel:
            if before.channel and before.channel.name == SessionEnvironment.start_label:
                # ignore multiple calls from the same person
                return
            if after.channel.name == SessionEnvironment.start_label:
                if len(after.channel.members) == 1:
                    session = await tools.get_session(after.channel, self.bot)
                    asyncio.create_task(session.start_session())
