import asyncio
from abc import ABC

from discord.ext import commands


# Bot Client Class
class SenseiClient(commands.AutoShardedBot, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # stores all dojos of connected guilds
        self.dojos = {}
        self.topgg = None
        self.log = None

    def get_dojo(self, guild_id):
        return self.dojos.get(guild_id, None)

    # statistics
    @property
    def dojo_count(self):
        return len(self.dojos)

    @property
    def session_count(self):
        return sum([len(dojo.active_sessions.values()) for dojo in self.dojos.values()])

    @property
    def active_users(self):
        return sum([dojo.active_users for dojo in self.dojos.values()])

    async def close(self):
        """ exit the whole application safely """
        print("Shutdown Sensei Doro... ")
        if self.topgg:
            self.topgg.update_stats.stop()
        if self.log:
            self.log.update_stats.stop()
        # todo: close all active sessions and notify users about shutdown
        # todo: cleanup session environments
        await super().close()
        await asyncio.sleep(1)

