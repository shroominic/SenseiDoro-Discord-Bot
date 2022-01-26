from discord.ext import commands


# Bot Client Class
class SenseiClient(commands.Bot):
    def __init__(self, *args, **options):
        super(SenseiClient, self).__init__(*args, **options)
        # stores all dojos of connected guilds
        self.dojos = {}
