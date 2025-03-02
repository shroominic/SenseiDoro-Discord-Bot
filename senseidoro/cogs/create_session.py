import discord
from discord import app_commands
from discord.ext import commands

from senseidoro.session import Session


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
    async def create_session(
        self,
        interaction: discord.Interaction,
        name: str,
        work_time: int = 25,
        break_time: int = 5,
        repetitions: int = 4,
    ) -> None:
        # Validate input parameters
        if not interaction.guild_id:
            await interaction.response.send_message(
                "This command can only be used in a server", ephemeral=True
            )
            return

        if work_time < 1 or work_time > 120:
            await interaction.response.send_message(
                "Work time must be between 1 and 120 minutes", ephemeral=True
            )
            return

        if break_time < 1 or break_time > 60:
            await interaction.response.send_message(
                "Break time must be between 1 and 60 minutes", ephemeral=True
            )
            return

        if repetitions < 1 or repetitions > 10:
            await interaction.response.send_message(
                "Number of repetitions must be between 1 and 10", ephemeral=True
            )
            return

        # Defer the response since creating channels might take a while
        await interaction.response.defer()

        try:
            # Create new session
            session = await Session.create(
                bot=self.bot,
                guild_id=interaction.guild_id,
                name=name,
                work_time=work_time,
                break_time=break_time,
                repetitions=repetitions,
            )

            if not session.env.info_channel:
                await interaction.followup.send(
                    "Failed to create session: Could not create info channel",
                    ephemeral=True,
                )
                return

            await interaction.followup.send(
                f"Created new session: {name}\n"
                f"Work time: {work_time} minutes\n"
                f"Break time: {break_time} minutes\n"
                f"Repetitions: {repetitions}\n"
                f"Head over to {session.env.info_channel.mention} to start the session!",
                ephemeral=True,
            )

        except Exception as e:
            await interaction.followup.send(
                f"Failed to create session: {str(e)}", ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CreateSession(bot))
