import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import logging
from datetime import datetime

from ..db import get_db

logger = logging.getLogger(__name__)


class RegisterOldServers(commands.Cog):
    """Handles registration and initialization of old servers"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.initialized = False  # Prevent multiple initializations

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Initialize bot and register unregistered servers when ready"""
        if self.initialized:
            return

        await self.register_all_unregistered_servers()
        self.initialized = True

    @app_commands.command(
        name="register",
        description="Manually register or re-register this server with Sensei Doro",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def register_command(self, interaction: discord.Interaction) -> None:
        """Manually register or re-register a server"""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server!"
            )
            return

        await interaction.response.defer()

        try:
            await self.initialize_server(interaction.guild)
            await interaction.followup.send("✅ Server registration complete!")
        except Exception as e:
            logger.error(f"Error during manual registration: {str(e)}")
            await interaction.followup.send(
                "❌ An error occurred during registration. Please check the logs or try again later."
            )

    async def get_unregistered_servers(self) -> list[discord.Guild]:
        """Get list of servers that aren't registered in the database"""
        conn = get_db()
        cursor = conn.cursor()

        # Get all registered server IDs
        cursor.execute("SELECT server_id FROM servers")
        registered_ids = {row[0] for row in cursor.fetchall()}

        # Find servers that aren't registered
        unregistered_servers = [
            guild for guild in self.bot.guilds if guild.id not in registered_ids
        ]

        conn.close()
        return unregistered_servers

    async def find_existing_sessions(
        self, guild: discord.Guild
    ) -> list[tuple[discord.TextChannel, discord.VoiceChannel]]:
        """Find all existing Pomodoro session setups in a guild"""
        sessions: list[tuple[discord.TextChannel, discord.VoiceChannel]] = []
        dashboards: list[discord.TextChannel] = []
        lobbies: list[discord.VoiceChannel] = []

        for channel in guild.channels:
            if (
                isinstance(channel, discord.TextChannel)
                and channel.name == "📋dashboard"
            ):
                # Verify it has a message from the bot
                try:
                    async for message in channel.history(limit=1):
                        if message.author == self.bot.user:
                            dashboards.append(channel)
                            break
                except discord.Forbidden:
                    continue

            elif (
                isinstance(channel, discord.VoiceChannel) and channel.name == "☕ lobby"
            ):
                lobbies.append(channel)

        # Match each dashboard with the closest lobby by position
        for dashboard in dashboards:
            closest_lobby = None
            min_distance = float("inf")

            for lobby in lobbies:
                # Simple distance metric - difference in position
                distance = abs(dashboard.position - lobby.position)
                if distance < min_distance:
                    min_distance = distance
                    closest_lobby = lobby

            if closest_lobby:
                sessions.append((dashboard, closest_lobby))

        return sessions

    async def register_existing_session(
        self,
        guild: discord.Guild,
        dashboard: discord.TextChannel,
        lobby: discord.VoiceChannel,
    ) -> None:
        """Register an existing Pomodoro session in the database"""
        if not self.bot.user:
            return

        conn = get_db()
        cursor = conn.cursor()
        try:
            # Add session to database with default settings
            cursor.execute(
                """
                INSERT INTO sessions (
                    server_id, 
                    info_channel_id, 
                    lobby_channel_id,
                    started_by_user_id, 
                    start_time,
                    name,
                    status,
                    settings
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    guild.id,
                    dashboard.id,
                    lobby.id,
                    self.bot.user.id,
                    datetime.utcnow(),
                    "Pomodoro",  # Default name
                    "active",
                    '{"mute_admins": true, "work_time": 25, "break_time": 5, "repetitions": 4}',
                ),
            )
            session_id = cursor.lastrowid

            # Log the session creation
            logger.info(
                f"✅ Registered existing session (ID: {session_id}) in {guild.name}"
            )

            # Initialize session participants for any members currently in the lobby
            for member in lobby.members:
                cursor.execute(
                    """
                    INSERT INTO session_participants (
                        session_id, 
                        user_id, 
                        join_time
                    ) VALUES (?, ?, ?)
                    """,
                    (session_id, member.id, datetime.utcnow()),
                )

            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"❌ Error registering session for {guild.name}: {str(e)}")
            # Attempt to rollback if there was an error
            try:
                conn.rollback()
            except sqlite3.Error:
                pass
        finally:
            conn.close()

    async def initialize_server(self, guild: discord.Guild) -> None:
        """Initialize a server in the database and set up required channels"""
        logger.info(f"🔄 Initializing server: {guild.name} ({guild.id})")

        # Add server to database
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO servers (server_id, server_name) VALUES (?, ?)",
                (guild.id, guild.name),
            )
            conn.commit()
            logger.info(f"✅ Added {guild.name} to database")

            # Check for existing Pomodoro setups
            existing_sessions = await self.find_existing_sessions(guild)
            if existing_sessions:
                for dashboard, lobby in existing_sessions:
                    await self.register_existing_session(guild, dashboard, lobby)
            else:
                # Find or create necessary channels
                system_channel = guild.system_channel or next(
                    (
                        channel
                        for channel in guild.text_channels
                        if channel.permissions_for(guild.me).send_messages
                    ),
                    None,
                )

                if system_channel:
                    await system_channel.send(
                        "👋 Hello! I've just initialized Sensei Doro for this server.\n"
                        "Use `/welcome` to see how to get started!"
                    )
                    logger.info(f"✅ Sent welcome message to {guild.name}")

        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ Server {guild.name} already in database")
        except Exception as e:
            logger.error(f"❌ Error initializing {guild.name}: {str(e)}")
        finally:
            conn.close()

    async def register_all_unregistered_servers(self) -> None:
        """Register all unregistered servers"""
        logger.info("\n🔍 Checking for unregistered servers...")
        unregistered_servers = await self.get_unregistered_servers()

        if not unregistered_servers:
            logger.info("✅ All servers are registered!")
            return

        logger.info(f"📝 Found {len(unregistered_servers)} unregistered servers")
        for guild in unregistered_servers:
            if guild.id == 979746895985528863 or guild.id == 1255242218160259072:
                await guild.leave()
            await self.initialize_server(guild)

        logger.info("✨ Server initialization complete!")


async def setup(bot: commands.Bot):
    await bot.add_cog(RegisterOldServers(bot))
