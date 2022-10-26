import asyncio
import os

from discord import Embed
from dotenv import load_dotenv
from discord.ext import commands, tasks


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # load token from .env
        load_dotenv()
        self.logging_token = os.getenv('LOGGING_TOKEN')
        #
        self.manager_id = None
        self.stats_embed = None

    async def update_manager_id(self):
        if self.manager_id is None:
            self.manager_id = await self.bot.fetch_user(self.logging_token)
        return self.manager_id

    @tasks.loop(minutes=1)
    async def update_stats(self):
        """ This function runs every 1 minutes for logging sensei doro stats to manager. """
        if self.stats_embed:
            await self.stats_embed.edit(embed=self.sensei_stats_embed)
        elif self.manager_id:
            self.stats_embed = await self.manager_id.send(embed=self.sensei_stats_embed)
        else:
            await self.manage_sensei_stats()

    def send_log(self, title, body="", color=0x000000):
        """ sends a log to the logging channel """
        if self.manager_id:
            embed = Embed(title=title, description=body, color=color)
            asyncio.create_task(self.manager_id.send(embed=embed))

    def exception(self, exception_ctx, exception_body, color=0xff0000):
        """ sends an exception to the logging channel """
        self.send_log(f"Exception: {exception_ctx}", exception_body)

    @property
    def sensei_stats_embed(self):
        """ creates a embed for all sensei stats """
        embed = Embed(title="Sensei Stats")
        # number of dojos
        embed.add_field(name="Total Dojos",
                        value=f"{self.bot.total_dojos}")
        # number of all created sessions
        embed.add_field(name="Total Sessions",
                        value=f"{self.bot.total_sessions}")
        # number of running sessions
        embed.add_field(name="Active Sessions",
                        value=f"{self.bot.total_active_sessions}")
        # number of users inside active sessions
        embed.add_field(name="Active Users",
                        value=f"{self.bot.total_active_users}")
        # number of sessions running in the last 24 hours
        embed.add_field(name="Sessions per 24h",
                        value=f"{self.bot.total_sessions_24h}")
        # number of active users in the last 24 hours
        embed.add_field(name="Users per 24h",
                        value=f"{self.bot.total_active_users_24h}")
        # todo add more stats
        return embed

    async def manage_sensei_stats(self):
        """ manages the sensei stats embed """
        await self.update_manager_id()
        embeds = [msg async for msg in self.manager_id.history()
                  if msg.embeds for embed in msg.embeds
                  if "Sensei Stats" in embed.title]
        if len(embeds) == 0:
            self.stats_embed = await self.manager_id.send(embed=self.sensei_stats_embed)
        else:
            for embed in embeds[1:]:
                await embed.delete()
            self.stats_embed = embeds[0]
            await self.stats_embed.edit(embed=self.sensei_stats_embed)
