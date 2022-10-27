import asyncio
import sqlite3
from contextlib import closing

import discord


class SessionEnvironment:
    # default channel labels
    info_label = "📋dashboard"
    lobby_label = "☕️ lobby"
    work_label = "⏳ focus"

    def __init__(self, guild, **kwargs):
        self.guild = guild
        # category
        self.category = kwargs.get("category", None)
        # voice channels
        self.lobby_channel = kwargs.get("lobby_channel", None)
        self.work_channel = kwargs.get("work_channel", None)
        # chat channels
        self.info_channel = kwargs.get("info_channel", None)
        self.chat_channel = kwargs.get("chat_channel", None)  # should get removed soon
        self.config_channel = kwargs.get("config_channel", None)  # should get removed soon
        # msg references
        self.info_msg = kwargs.get("info_msg", None)
        self.timer_msg = kwargs.get("timer_msg", None)
        self.config_msg = kwargs.get("config_msg", None)  # should get removed soon

    @classmethod
    def create_new(cls, guild, session_name):
        # create empty environment
        env = cls(guild)
        # create env asynchronously
        asyncio.create_task(env.async_create_new(session_name))
        # return env class object
        return env

    @classmethod
    def from_database(cls, category_id, bot):
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM sessions WHERE id=:id", {"id": category_id})
            result = c.fetchone()
            category = bot.get_channel(category_id)
            guild = category.guild
            references = {"category": category,
                          "info_channel": bot.get_channel(result[3]),
                          "lobby_channel": bot.get_channel(result[4])}
            # create environment
            env = cls(guild, **references)
            # asynchronous message matching
            asyncio.create_task(env.async_match_messages(bot.user))
            asyncio.create_task(env.remove_old_env_on_bot_restart())
            return env

    @classmethod
    def match_from_category(cls, category, bot):
        references = {"category": category}
        # match voice_channels
        for vc in category.voice_channels:
            channel_name = vc.name
            if "Lobby" in channel_name:
                references["lobby_channel"] = vc
            if "START" in channel_name or "Session" in channel_name or "Break" in channel_name:
                references["work_channel"] = vc
        # match text_channels
        for tc in category.text_channels:
            channel_name = tc.name
            if "chat" in channel_name:
                references["chat_channel"] = tc
            if "info" in channel_name:
                references["info_channel"] = tc
            if "config" in channel_name:
                references["config_channel"] = tc
        # create environment
        env = cls(category.guild, **references)
        # information for aborted active sessions
        if references["work_channel"].name != "START SESSION":
            embed = discord.Embed(title="Session Aborted")
            embed.description = "Due to a server restart this session has been reset."
            asyncio.create_task(references["chat_channel"].send(embed=embed, delete_after=60))
        return env

    async def session_setup(self):
        # todo remove config check if update complete
        if self.config_channel:
            print("config channel exists")
            return

    async def create_work_channel(self):
        """ Creates a work channel for the session """
        work_ow = {self.guild.self_role: discord.PermissionOverwrite(connect=True, view_channel=True),
                   self.guild.default_role: discord.PermissionOverwrite(speak=False, view_channel=False)}
        self.work_channel = await self.guild.create_voice_channel(self.work_label,
                                                                  category=self.category,
                                                                  overwrites=work_ow)

    async def remove_old_env_on_bot_restart(self):
        # delete old unused voice channels
        for vc in self.category.voice_channels:
            if "Session [" in vc.name:
                await vc.delete()
        # remove old timer message
        if self.timer_msg:
            await self.timer_msg.delete()
            self.timer_msg = None

    async def async_create_new(self, session_name):
        # create session category
        category = await self.guild.create_category_channel(session_name)
        # create initial channels
        info_ow = {
            self.guild.self_role: discord.PermissionOverwrite(send_messages=True, view_channel=True),
            self.guild.default_role: discord.PermissionOverwrite(send_messages=False),
        }
        self.info_channel = await self.guild.create_text_channel(self.info_label, category=category, overwrites=info_ow)
        self.lobby_channel = await self.guild.create_voice_channel(self.lobby_label, category=category)
        # load env ids to database - create whole new entry? todo
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            print("database update")
            c.execute("UPDATE sessions SET info_channel_id = :info_id WHERE id = :id",
                      {"info_id": self.info_channel.id, "id": category.id})
            c.execute("UPDATE sessions SET lobby_channel_id = :lobby_id WHERE id = :id",
                      {"lobby_id": self.lobby_channel.id, "id": category.id})
            conn.commit()
        self.category = category

    async def async_match_messages(self, bot_user):
        # match msg references
        if self.config_channel:
            async for msg in self.config_channel.history():
                if msg.author == bot_user and msg.content.startswith('Session config:'):
                    self.config_msg = msg
        if self.info_channel:
            async for msg in self.info_channel.history():
                if msg.embeds:
                    for embed in msg.embeds:
                        if embed.fields:
                            for field in embed.fields:
                                if "Dashboard" in field.name:
                                    self.info_msg = msg
                        if "timer" in embed.title:
                            self.timer_msg = msg

    async def update_environment(self):
        await self.category.edit(name=self.category.name[1:])
        await self.info_channel.edit(name=self.info_label)
        await self.work_channel.edit(name=self.work_label)
        await self.chat_channel.delete()
        await self.config_channel.delete()

    async def dispose(self):
        # delete all channels
        await self.info_channel.delete()
        await self.lobby_channel.delete()
        await self.category.delete()

    @property
    def info_channel_id(self):
        return self.info_channel.id if self.info_channel else None

    @property
    def lobby_channel_id(self):
        return self.lobby_channel.id if self.lobby_channel else None

    # todo cmd to create old env for testing
