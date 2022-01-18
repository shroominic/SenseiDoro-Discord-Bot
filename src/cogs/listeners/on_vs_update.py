
from discord.ext.commands import Cog
import asyncio

from src.models.session import Session


class OnVSUpdate(Cog, name='OnVSUpdate module'):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        This function gets called, when something changes in voice channels.
        """
        if before.channel is not None:
            if before.channel.name == Session.start_button_name:
                # only workaround?
                return
        if after.channel is not None:
            if after.channel.name == Session.start_button_name:
                session = await Session.get_session(after.channel, self.bot)
                asyncio.create_task(session.start_session(member))
