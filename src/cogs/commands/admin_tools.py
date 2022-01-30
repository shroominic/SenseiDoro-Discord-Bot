import asyncio

from discord.ext import commands


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role("Dojo Manager")
    async def cleanup(self, ctx):
        """
        Removes all Session environments from the bot.
        :param ctx: context of command
        """
        # get dojo reference
        for category in ctx.guild.categories:
            if "🍅" in category.name:
                # delete all channels inside category
                for vc in category.voice_channels:
                    await vc.delete()
                for tc in category.text_channels:
                    await tc.delete()
                # delete category
                await category.delete()

    @commands.command()
    @commands.has_any_role("Dojo Manager")
    async def delete(self, ctx, to_delete=""):
        """
        Deletes all messages in the text channel where called.
        :param ctx: context of command
        :param to_delete: keyword argument
        """
        if "messages" in to_delete:
            await ctx.send("I'll delete all messages for you!")
            # delete all messages inside message.channel
            async for msg in ctx.channel.history():
                asyncio.create_task(msg.delete())
        elif "sessions" in to_delete:
            await ctx.send("I'll delete all sessions for you!")
            # get dojo reference
            dojo = self.bot.dojos[ctx.guild.id]
            # delete all sessions in ctx.guild
            for session in dojo.sessions.values():
                asyncio.create_task(session.dispose())
        else:
            await ctx.send("Type '$delete <messages/sessions>'")

