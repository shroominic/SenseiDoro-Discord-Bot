import asyncio

from discord.ext import commands

from src.cogs.commands import cmd_helper


class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cleanup(self, ctx):
        """
        Removes all Session environments from the bot.
        :param ctx: context of command
        """
        # cmd only for admins
        role = self.bot.dojos[ctx.guild.id].admin_role
        if role in ctx.author.roles:
            # command feedback
            title = "Okay sir I'll clean your room!"
            asyncio.create_task(cmd_helper.feedback(ctx, title))
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
        else:
            title = "Missing Role"
            feedback = "You need to have the admin role to use this command."
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))

    @commands.command()
    @commands.has_any_role("Dojo Manager")
    async def delete(self, ctx, to_delete=""):
        """
        Deletes all messages in the text channel where called.
        :param ctx: context of command
        :param to_delete: keyword argument
        """
        # cmd only for admins
        role = self.bot.dojos[ctx.guild.id].admin_role
        if role in ctx.author.roles:
            if "messages" in to_delete:
                # delete all messages inside message.channel
                async for msg in ctx.channel.history():
                    asyncio.create_task(msg.delete())
                # command feedback
                title = "Okay sir I'll delete your messages!"
                asyncio.create_task(cmd_helper.feedback(ctx, title))

            elif "sessions" in to_delete:
                # command feedback
                title = "Okay sir I'll delete your sessions!"
                asyncio.create_task(cmd_helper.feedback(ctx, title))
                # get dojo reference
                dojo = self.bot.dojos[ctx.guild.id]
                # delete all sessions in ctx.guild
                for session in dojo.sessions.values():
                    asyncio.create_task(session.dispose())

            else:
                # error
                title = "Wrong argument"
                feedback = "Try '$delete <messages/sessions>'"
                asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
        else:
            # error
            title = "Missing Role"
            feedback = "You need to have the admin role to use this command."
            asyncio.create_task(cmd_helper.feedback(ctx, title, feedback))
