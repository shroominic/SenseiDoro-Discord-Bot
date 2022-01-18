import asyncio

from discord.ext import commands


class Tools(commands.Cog, name='Tools module'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cleanup(self, ctx):
        """
        Removes all Session environments from the bot. (TODO: Only in a server)
        """
        asyncio.create_task(ctx.send("Yeah mom, I'll cleanup my room very soon!"))
        # deletes active sessions
        for sees in self.bot.sessions:
            asyncio.create_task(sees.dispose())

    @commands.command()
    async def delete(self, ctx, to_delete=""):
        """
        Deletes all messages in the text channel where called.
        """
        if "messages" in to_delete:
            await ctx.send("I'll delete all messages for you!")
            # delete all messages inside message.channel
            async for msg in ctx.channel.history(limit=100):
                asyncio.create_task(msg.delete())
        else:
            await ctx.send("Type '$delete messages'")

