from abc import ABC

from discord.ext import commands


# Bot Client Class
class SenseiClient(commands.Bot, ABC):
    def __init__(self, **options):
        super().__init__(**options)
        # stores all dojos of connected guilds
        self.dojos = {}
