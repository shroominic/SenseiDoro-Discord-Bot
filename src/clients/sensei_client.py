from abc import ABC

from discord.ext import commands


# Bot Client Class
class SenseiClient(commands.AutoShardedBot, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # stores all dojos of connected guilds
        self.dojos = {}

    def get_dojo(self, guild_id):
        return self.dojos.get(guild_id, None)

