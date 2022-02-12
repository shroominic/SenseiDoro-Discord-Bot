
from discord.ext.commands import Cog
import asyncio

from src.session import Session, tools


class OnVSUpdate(Cog, name='OnVSUpdate module'):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        This function gets called, when something changes in voice channels.
        :param member: addressed member
        :param before: state before update
        :param after: state after update
        """

        if after.channel:
            if before.channel and before.channel.name == Session.start_button_label:
                # remove multiple calls from the same person
                return

            if after.channel.name == Session.start_button_label:
                if len(after.channel.members) == 1:
                    session = await tools.get_session(after.channel, self.bot)
                    asyncio.create_task(session.start_session(member))
