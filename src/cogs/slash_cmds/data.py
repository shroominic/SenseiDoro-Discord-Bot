import asyncio

from discord import SlashCommandGroup, slash_command

from cogs.better_response import slash_response
from src.cogs.useful_decoration import admin_required, default_feedback


class Data(SlashCommandGroup):
    def __init__(self, bot):
        super().__init__(name="data", description="Configure the data Sensei Doro knows about you.")
        self.bot = bot

    @slash_command()
    @admin_required
    @default_feedback(title="Data reset", description="All data is reset as if the bot is new on the server.")
    async def reset(self, ctx):
        # get dojo reference
        dojo = self.bot.dojos[ctx.guild.id]
        # update instance
        await dojo.reset_data()

    @slash_command()
    @admin_required
    async def delete(self, ctx):
        title = "Confirm the deletion of ALL DATA"
        description = """
            React with ✅ to confirm deletion.
            
            This will delete:
            - all configuration and settings
            - all sessions on this server
            
            Sensei Doro will leave the server afterwards.
            
            Consider using `/data reset` if you only want to reset your data.
            """
        slash_response(ctx, title, description, 60)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '✅'

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Sorry, this took to long for me. Try again!', delete_after=5)
        else:
            # get dojo reference
            dojo = self.bot.dojos[ctx.guild.id]
            # dojo delete
            await dojo.dispose()

