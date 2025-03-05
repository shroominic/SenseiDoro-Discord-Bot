import discord
from discord import app_commands
from discord.ext import commands

from ..session import create_session


class CreateSession(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="create", description="Create a new study session")
    @app_commands.describe(
        name="Name of the session",
        work_time="Work duration in minutes (default: 25)",
        break_time="Break duration in minutes (default: 5)",
        repetitions="Number of work sessions (default: 4)",
    )
    async def create_session_command(
        self,
        interaction: discord.Interaction,
        name: str,
        work_time: int = 25,
        break_time: int = 5,
        repetitions: int = 4,
    ) -> None:
        if work_time < 1 or work_time > 120:
            await interaction.response.send_message("⚠️ Work time must be between 1 and 120 minutes", ephemeral=True)
            return

        if break_time < 1 or break_time > 60:
            await interaction.response.send_message("⚠️ Break time must be between 1 and 60 minutes", ephemeral=True)
            return

        if repetitions < 1 or repetitions > 10:
            await interaction.response.send_message("⚠️ Repetitions must be between 1 and 10", ephemeral=True)
            return

        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            await create_session(self.bot, interaction.guild.id, name, work_time, break_time, repetitions)

            await interaction.followup.send(
                f"✅ Session **{name}** created successfully!\n\n"
                f"⏱️ Work: {work_time} minutes\n"
                f"☕️ Break: {break_time} minutes\n"
                f"🔄 Repetitions: {repetitions}\n\n"
                f"Check your new channels for the dashboard.",
                ephemeral=True,
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Error creating session: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CreateSession(bot))
