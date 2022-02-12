import discord
from discord.ext import tasks

from . import env_manager
from .timer import Timer
import asyncio
import json


# Pomodoro Session Class
class Session:
    # channel labels
    start_button_label = "START SESSION"
    break_time_label = "Break time!"
    information_label = "info"
    config_label = "config"
    lobby_label = "Lobby"
    chat_label = "chat"

    def __init__(self,
                 dojo,
                 category,
                 work_time,
                 break_time,
                 repetitions,
                 is_new_session,
                 session_name="Pomodoro"
                 ):
        self.name = session_name
        self.label = f"🍅 {self.name}"
        # references
        self.dojo = dojo
        self.category_pointer = category
        self.info_channel_pointer = None
        self.chat_channel_pointer = None
        self.work_channel_pointer = None
        self.lobby_channel_pointer = None
        self.config_channel_pointer = None
        self.info_msg_embed = None
        self.config_msg = None
        # timer settings
        self.timer = Timer(self, work_time, break_time, repetitions)
        # async init
        asyncio.create_task(self.init(is_new_session))

    async def init(self, is_new_session):
        # initializes the session category and channels
        await env_manager.create_environment(is_new_session, self)
        # list session instance inside dojo.sessions dict
        self.dojo.sessions[self.category_pointer.id] = self
        # creates information embed
        if not self.info_msg_embed:
            info_embed = self.get_info_embed()
            self.info_msg_embed = await self.info_channel_pointer.send(embed=info_embed)

    #############
    #   START   #
    #############

    async def start_session(self, member):
        # close session so no one can join during work_time
        asyncio.create_task(self.work_channel_pointer.set_permissions(self.dojo.guild.me,
                                                                      connect=True))
        asyncio.create_task(self.work_channel_pointer.set_permissions(self.dojo.guild.default_role,
                                                                      connect=False, speak=False))
        # init session
        if member.guild_permissions.administrator and self.dojo.mute_admins:
            await member.edit(mute=True)
        # start session timer
        asyncio.create_task(self.timer.start_timer())
        # start auto reset task
        if not self.reset_if_empty.is_running():
            self.reset_if_empty.start()
        else:
            self.reset_if_empty.restart()

    ##################
    #   NAVIGATION   #
    ##################

    async def next_session(self):
        asyncio.create_task(self.update_info_embed())
        # rename session
        session_name = f"Session [ {self.timer.session_count} | {self.timer.repetitions} ]"
        await self.work_channel_pointer.edit(name=session_name)
        # move all members from lobby to session
        for member in self.lobby_channel_pointer.members:
            await member.move_to(self.work_channel_pointer)
            # admins do not get muted automatically
            if member.guild_permissions.administrator and self.dojo.mute_admins:
                await member.edit(mute=True)

    async def take_a_break(self):
        # move members to lobby and unmute admins
        label = self.break_time_label
        await self.reset_members_and_work_channel(label)

    async def force_break(self, minutes):
        # current session don't count
        if self.timer.session_count > 0:
            self.timer.session_count -= 1
        asyncio.create_task(self.update_info_embed())
        # self.timer.break_time as default value
        if minutes > 120:
            # start normal break
            self.timer.set_time_left(0)
        else:
            # set (new) break_time
            temp = self.timer.break_time
            self.timer.break_time = minutes
            # start a (minutes long) break
            self.timer.set_time_left(0)

            async def set_old_break_time():
                await asyncio.sleep(self.timer.tick)
                self.timer.break_time = temp
                asyncio.create_task(self.update_info_embed())

            asyncio.create_task(set_old_break_time())

    async def reset_session(self):
        # resets
        self.timer.reset()
        self.reset_if_empty.stop()
        await self.reset_members_and_work_channel(self.start_button_label)
        # delete timer msg
        if self.timer.info_msg:
            await self.timer.info_msg.delete()
            self.timer.info_msg = None
        # clear info_channel
        async for msg in self.info_channel_pointer.history():
            if msg == self.info_msg_embed:
                continue
            else:
                await msg.delete()
        # edit/create info embed
        info_embed = self.get_info_embed()
        if self.info_msg_embed:
            await self.info_msg_embed.edit(embed=info_embed)
        else:
            self.info_msg_embed = await self.info_channel_pointer.send(embed=info_embed)

    ###############
    #    TOOLS    #
    ###############

    @property
    def member_count(self) -> int:
        return len(self.lobby_channel_pointer.members) + len(self.work_channel_pointer.members)

    @property
    async def is_empty(self) -> bool:
        if self.member_count == 0:
            await asyncio.sleep(10)
            return self.member_count == 0
        return False

    @tasks.loop(minutes=1)
    async def reset_if_empty(self):
        if await self.is_empty:
            asyncio.create_task(self.reset_session())

    async def reset_members_and_work_channel(self, work_channel_label):
        """ move all members back to lobby and unmute admins """
        for member in self.work_channel_pointer.members:
            await member.move_to(self.lobby_channel_pointer)
            # admins do not get unmuted automatically
            if member.guild_permissions.administrator:
                await member.edit(mute=False)
        # only relevant if admin leaves the session early
        for member in self.lobby_channel_pointer.members:
            if member.guild_permissions.administrator:
                await member.edit(mute=False)
        # reset work_channel
        if self.work_channel_pointer:
            await self.work_channel_pointer.delete()
        work_ow = {
            self.dojo.guild.default_role: discord.PermissionOverwrite(speak=False)
        }
        self.work_channel_pointer = await self.dojo.guild.create_voice_channel(
            work_channel_label,
            category=self.category_pointer,
            overwrites=work_ow
        )

    def get_info_embed(self):
        """ return info_embed: creates an embed with session information """
        info_embed = discord.Embed(title=self.name)
        info_embed.add_field(name="work time", value=f"{self.timer.work_time} min")
        info_embed.add_field(name="break time", value=f"{self.timer.break_time} min")
        info_embed.add_field(name="session", value=f"[ {self.timer.session_count} | {self.timer.repetitions} ]")
        return info_embed

    async def update_info_embed(self):
        """ updates the information message """
        info_embed = self.get_info_embed()
        await self.info_msg_embed.edit(embed=info_embed)

    async def update_edit(self):
        self.label = f"🍅 {self.name}"
        if self.category_pointer.name != self.label:
            await self.category_pointer.edit(name=self.label)
        await self.update_info_embed()
        # update config
        await self.config_msg.edit(f"Session config: {self.to_json()}")

    async def dispose(self):
        # turn timer off
        self.timer.is_active = False
        # delete channels
        for vc in self.category_pointer.voice_channels:
            await vc.delete()
        for tc in self.category_pointer.text_channels:
            await tc.delete()
        del self.dojo.sessions[self.category_pointer.id]
        await self.category_pointer.delete()

    def to_json(self):
        """
        serializes important information to json string
        """
        return json.dumps({
            "name": self.name,
            "work_time": self.timer.work_time,
            "pause_time": self.timer.break_time,
            "number_sessions": self.timer.repetitions
        })

    def __eq__(self, other):
        return self.name == other.name
