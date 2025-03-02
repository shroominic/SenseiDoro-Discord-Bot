from __future__ import annotations
import asyncio
import discord
from discord.ext import tasks


class SessionEnvironment:
    """Manages the Discord channels and categories for a session"""

    INFO_LABEL = "📋dashboard"
    LOBBY_LABEL = "☕️ lobby"
    WORK_LABEL = "⏳focus"

    def __init__(self, guild: discord.Guild) -> None:
        self.guild = guild
        self.category: discord.CategoryChannel | None = None
        self.info_channel: discord.TextChannel | None = None
        self.lobby_channel: discord.VoiceChannel | None = None
        self.work_channel: discord.VoiceChannel | None = None

    async def check_permissions(self) -> bool:
        """Check if bot has necessary permissions to create channels for the session environment"""
        bot_member = self.guild.me
        required_permissions = discord.Permissions(
            manage_channels=True,  # Needed to create channels
            view_channel=True,  # Needed to see channels
            manage_roles=True,  # Needed to set channel permissions
        )

        # Check if bot has the required permissions
        missing_permissions = [
            perm
            for perm, value in required_permissions
            if value and not getattr(bot_member.guild_permissions, perm)
        ]

        if missing_permissions:
            error_message = (
                f"Missing required permissions: {', '.join(missing_permissions)}. "
                f"Please grant these permissions to the bot to create session environments."
            )

            # Try to notify in guild system channel if available
            if (
                self.guild.system_channel
                and self.guild.system_channel.permissions_for(bot_member).send_messages
            ):
                await self.guild.system_channel.send(error_message)
            # Otherwise try to DM the guild owner
            elif self.guild.owner:
                try:
                    await self.guild.owner.send(
                        f"In server '{self.guild.name}': {error_message}"
                    )
                except discord.Forbidden:
                    # Cannot DM the owner, permissions will still return False
                    pass

            return False

        return True

    async def create(self, name: str) -> None:
        """Create the initial session environment"""
        if not await self.check_permissions():
            return

        self.category = await self.guild.create_category_channel(name)

        if not self.guild.self_role or not self.guild.default_role:
            raise ValueError("Could not find required guild roles")

        info_overwrites: dict[
            discord.Role | discord.Member, discord.PermissionOverwrite
        ] = {
            self.guild.self_role: discord.PermissionOverwrite(
                send_messages=True, view_channel=True
            ),
            self.guild.default_role: discord.PermissionOverwrite(send_messages=False),
        }
        self.info_channel = await self.guild.create_text_channel(
            self.INFO_LABEL,
            category=self.category,
            overwrites=info_overwrites,
        )

        self.lobby_channel = await self.guild.create_voice_channel(
            self.LOBBY_LABEL, category=self.category
        )

    async def create_work_channel(self) -> None:
        """Create the work channel with appropriate permissions"""
        if not self.category:
            raise ValueError("Could not find category for work channel")

        if not self.guild.self_role or not self.guild.default_role:
            raise ValueError("Could not find required guild roles")

        work_overwrites: dict[
            discord.Role | discord.Member, discord.PermissionOverwrite
        ] = {
            self.guild.self_role: discord.PermissionOverwrite(
                connect=True, view_channel=True
            ),
            self.guild.default_role: discord.PermissionOverwrite(
                speak=False, connect=False
            ),
        }

        self.work_channel = await self.guild.create_voice_channel(
            self.WORK_LABEL,
            category=self.category,
            overwrites=work_overwrites,
        )

    async def cleanup(self) -> None:
        if self.work_channel:
            await self.work_channel.delete()
            self.work_channel = None
        if self.lobby_channel:
            await self.lobby_channel.delete()
            self.lobby_channel = None
        if self.info_channel:
            await self.info_channel.delete()
            self.info_channel = None
        if self.category:
            await self.category.delete()
            self.category = None


class Session:
    """Manages a study session with work/break intervals"""

    def __init__(
        self,
        bot: discord.Client,
        guild_id: int,
        name: str,
        work_time: int,
        break_time: int,
        repetitions: int,
        mute_admins: bool = True,
    ) -> None:
        self.bot = bot
        self.guild_id = guild_id
        self.name = name
        self.work_time = work_time
        self.break_time = break_time
        self.repetitions = repetitions
        self.mute_admins = mute_admins

        guild = self.bot.get_guild(guild_id)
        if not guild:
            raise ValueError(f"Could not find guild with ID {guild_id}")

        self.env = SessionEnvironment(guild)
        self.session_count = 0
        self.time_left = 0
        self.is_break = False
        self.is_running = False

        # Start the empty session check
        self._check_empty.start()

    @classmethod
    async def create(
        cls,
        bot: discord.Client,
        guild_id: int,
        name: str,
        work_time: int,
        break_time: int,
        repetitions: int,
        mute_admins: bool = True,
    ) -> Session:
        """Create a new session with its environment"""
        session = cls(
            bot, guild_id, name, work_time, break_time, repetitions, mute_admins
        )
        await session.env.create(name)
        return session

    async def start(self) -> None:
        """Start the session timer"""
        if self.is_running:
            return

        self.is_running = True
        self.time_left = self.work_time * 60  # Convert to seconds
        self.session_count = 1

        await self._update_status()
        asyncio.create_task(self._timer_loop())

    async def stop(self) -> None:
        """Stop the current session"""
        self.is_running = False
        self.session_count = 0
        self.time_left = 0
        await self._reset_members()
        await self._update_status()

    async def force_break(self, minutes: int) -> None:
        """Force a break for the specified duration"""
        if minutes > 120:
            minutes = self.break_time

        if self.session_count > 0:
            self.session_count -= 1

        self.is_break = True
        self.time_left = minutes * 60
        await self._reset_members()
        await self._update_status()

    async def _timer_loop(self) -> None:
        """Main timer loop for the session"""
        while self.is_running and self.time_left > 0:
            await asyncio.sleep(1)
            self.time_left -= 1

            if self.time_left <= 0:
                if self.is_break:
                    # Break finished, start work
                    self.is_break = False
                    self.time_left = self.work_time * 60
                    await self.env.create_work_channel()
                else:
                    # Work finished, start break or end session
                    if self.session_count >= self.repetitions:
                        await self.stop()
                        return

                    self.session_count += 1
                    self.is_break = True
                    self.time_left = self.break_time * 60
                    await self._reset_members()

                await self._update_status()

    async def _reset_members(self) -> None:
        """Move members to lobby and handle unmuting"""
        if self.env.work_channel and self.env.lobby_channel:
            for member in self.env.work_channel.members:
                await member.move_to(self.env.lobby_channel)
                if member.guild_permissions.administrator and self.mute_admins:
                    await member.edit(mute=False)

            await self.env.work_channel.delete()
            self.env.work_channel = None

    async def _update_status(self) -> None:
        """Update the session status in the info channel"""
        if not self.env.info_channel:
            return

        minutes = self.time_left // 60
        seconds = self.time_left % 60

        status = "🔴 Session not started"
        if self.is_running:
            status = f"⏳ {'Break' if self.is_break else 'Work'} time: {minutes:02d}:{seconds:02d}"

        embed = discord.Embed(
            title="Study Session Status",
            description=f"**{self.name}**\n{status}",
            color=0x00FF00 if self.is_running else 0xFF0000,
        )

        embed.add_field(
            name="Session Progress",
            value=f"{self.session_count}/{self.repetitions}",
            inline=True,
        )

        embed.add_field(
            name="Settings",
            value=f"Work: {self.work_time}min\nBreak: {self.break_time}min",
            inline=True,
        )

        # Delete previous messages and send new status
        async for message in self.env.info_channel.history():
            await message.delete()
        await self.env.info_channel.send(embed=embed)

    @tasks.loop(seconds=10)
    async def _check_empty(self) -> None:
        """Check if the session is empty and clean up if needed"""
        if not self.env.lobby_channel:
            return

        total_members = len(self.env.lobby_channel.members)
        if self.env.work_channel:
            total_members += len(self.env.work_channel.members)

        if total_members == 0:
            await asyncio.sleep(30)  # Wait to confirm it's really empty

            # Check again after waiting
            total_members = len(self.env.lobby_channel.members)
            if self.env.work_channel:
                total_members += len(self.env.work_channel.members)

            if total_members == 0:
                await self.stop()
                await self.env.cleanup()
                self._check_empty.stop()
