from typing import Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands


class Admin(commands.Cog):
    """Admin commands for bot management"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reload")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        cog="The cog to reload. Leave empty to reload all cogs",
        sync="Whether to sync application commands after reloading",
    )
    async def reload(
        self,
        interaction: discord.Interaction,
        cog: Optional[Literal["onboarding", "admin"]] = None,
        sync: bool = True,
    ):
        """Reload one or all cogs"""
        await interaction.response.defer(ephemeral=True)

        async def reload_cog(cog_name: str) -> tuple[bool, str]:
            try:
                await self.bot.reload_extension(f"senseidoro.cogs.{cog_name}")
                return True, f"✅ Reloaded `{cog_name}`"
            except Exception as e:
                return False, f"❌ Error reloading `{cog_name}`: {str(e)}"

        if cog:
            success, message = await reload_cog(cog)
            if success and sync:
                await self.bot.tree.sync()
                message += "\n✅ Synced application commands"
        else:
            results = []
            for cog_name in ["onboarding", "admin"]:  # Add new cogs here
                success, msg = await reload_cog(cog_name)
                results.append(msg)

            if sync and any(msg.startswith("✅") for msg in results):
                await self.bot.tree.sync()
                results.append("✅ Synced application commands")

            message = "\n".join(results)

        await interaction.followup.send(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
