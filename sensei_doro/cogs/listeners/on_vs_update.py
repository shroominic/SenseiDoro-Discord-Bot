
from discord.ext.commands import Cog

from ...session import tools


class OnVSUpdate(Cog, name='OnVSUpdate module'):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_voice_state_update(self, _, before, after):
        """ This function gets called, when something changes in voice channels. """
        if after.channel:
            if before.channel and before.channel.id == after.channel.id:
                # ignore multiple calls from the same channel
                return
            dojo = self.bot.dojos[after.channel.guild.id]
            # init session if some1 joins LOBBY
            if after.channel.id in dojo.lobby_ids:
                # session gets activated
                await tools.activate_session(after.channel, dojo)
        else:
            # todo
            # some code that unmute admins if they leave
            # check if before.channel.category is a active session
            # if so check if the member (_) was in this session
            # remove member from session in 120 seconds so they have time to join back
            pass
