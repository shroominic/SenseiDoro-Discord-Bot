from abc import ABC

from discord.ext import commands
from discord.ext.commands.errors import CommandOnCooldown
from discord import ApplicationContext, CheckFailure, DiscordException, Embed


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

    async def close(self):
        """ exit the whole application safely """
        print("Shutdown Sensei Doro... ")
        # close all active sessions
        for dojo in self.dojos.values():
            for session in list(dojo.active_sessions.values()):
                try:
                    await session.close()
                    session.send_notification("🚧 Session closed due to server maintenance 🛠",
                                              "Sorry for the inconvenience, 🚁 we're back online soon!")
                except Exception as e:
                    self.log.exception(f"failed to close session", e)
        # stop all tasks
        if self.topgg:
            await self.topgg.close()
        if self.log:
            self.log.auto_refresh.stop()
        # shutdown the bot
        await super().close()
        print("Shutdown complete.")

    # statistics todo: move to different place
    @property
    def total_dojos(self):
        return len(self.dojos)

    @property
    def total_sessions(self):
        return sum([len(dojo.lobby_ids) for dojo in self.dojos.values()])

    @property
    def total_active_sessions(self):
        return sum([len(dojo.active_sessions.values()) for dojo in self.dojos.values()])

    @property
    def total_active_users(self):
        return sum([dojo.active_users for dojo in self.dojos.values()])

    @property
    def total_sessions_24h(self):
        return 0  # todo

    @property
    def total_users_24h(self):
        # todo
        return 0  # todo
