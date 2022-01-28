import discord

from . import env_manager
from .timer import Timer
import asyncio
import json


# Pomodoro Session Class
class Session:
    # channel labels
    start_button_label = "START SESSION"
    session_break_label = ""
    information_label = "information"
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
        # init session
        await member.edit(mute=True)
        # start session timer
        asyncio.create_task(self.timer.start_timer())

    ##################
    #   NAVIGATION   #
    ##################

    async def next_session(self):
        self.timer.increase_session_count()
        asyncio.create_task(self.update_info_embed())
        # rename session
        await self.work_channel_pointer.edit(name=f"Session [ {self.timer.session_count} | {self.timer.repetitions} ]")
        # move all members from lobby to session
        for member in self.lobby_channel_pointer.members:
            await member.move_to(self.work_channel_pointer)
            await member.edit(mute=True)

    async def take_a_break(self):
        # move and unmute all waiting members
        for member in self.work_channel_pointer.members:
            await member.move_to(self.lobby_channel_pointer)
            await member.edit(mute=False)
        # work channel break msg
        await self.work_channel_pointer.delete()
        self.work_channel_pointer = await self.dojo.guild.create_voice_channel(
            self.session_break_label,
            category=self.category_pointer
        )

    async def reset_session(self):
        # reset stats
        self.timer.reset()
        # move all back to lobby
        for member in self.work_channel_pointer.members:
            await member.move_to(self.lobby_channel_pointer)
            await member.edit(mute=False)
        for member in self.lobby_channel_pointer.members:
            await member.edit(mute=False)
        # start button
        await self.work_channel_pointer.delete()
        self.work_channel_pointer = await self.dojo.guild.create_voice_channel(
            self.start_button_label,
            category=self.category_pointer
        )
        # delete timer msg
        if self.timer.timer_info_pointer:
            await self.timer.timer_info_pointer.delete()

        # edit/create info embed
        info_embed = self.get_info_embed()
        if self.info_msg_embed:
            await self.info_msg_embed.edit(embed=info_embed)
        else:
            self.info_msg_embed = await self.info_channel_pointer.send(embed=info_embed)

    ###############
    #    TOOLS    #
    ###############

    def get_info_embed(self):
        info_embed = discord.Embed(title="Session info")
        info_embed.add_field(name="work time", value=f"{self.timer.work_time} min")
        info_embed.add_field(name="break time", value=f"{self.timer.break_time} min")
        info_embed.add_field(name="session", value=f"[ {self.timer.session_count} | {self.timer.repetitions} ]")
        return info_embed

    async def update_info_embed(self):
        info_embed = self.get_info_embed()
        await self.info_msg_embed.edit(embed=info_embed)

    async def update_edit(self):
        self.label = f"🍅 {self.name}"
        if self.category_pointer.name != self.label:
            await self.category_pointer.edit(name=self.label)
        await self.update_info_embed()

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
