import sqlite3
import discord
from discord.ext import tasks
from contextlib import closing

from .env_manager import SessionEnvironment
from .session_config import SessionConfig
from .timer import Timer
import asyncio


# Pomodoro Session Class
class Session:
    def __init__(self, bot, name, guild_id, work_time, break_time, repetitions, env, **kwargs):
        self.bot = bot
        self.name = name
        self.config = kwargs.get("config", SessionConfig())
        self.env = env
        # ids
        self.id = kwargs.get("category_id", None)
        self.guild_id = guild_id
        # timer
        self.timer = Timer(self, work_time, break_time, repetitions)
        # async init
        asyncio.create_task(self.async_init())

    async def async_init(self):
        # wait until environment is created
        while not (self.env.category or self.id):
            print("Category not created")  # todo remove debug print
            await asyncio.sleep(2)
        # set session id
        self.id = self.env.category.id
        # list session instance inside dojo.sessions dict
        self.dojo.bot.active_sessions[self.id] = self
        # creates information embed
        await asyncio.sleep(5)
        if not self.env.info_msg:
            info_embed = self.get_info_embed()
            self.env.info_msg = await self.env.info_channel.send(embed=info_embed)

    @classmethod
    def new_session(cls, bot, guild_id, name, work_time, break_time, repetitions):
        env = SessionEnvironment.create_new(bot.get_guild(guild_id), name)
        session_instance = cls(bot, name, guild_id, work_time, break_time, repetitions, env)
        session_instance.create_db_entry()
        return session_instance

    @classmethod
    def from_db(cls, session_id, bot):
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            # check if session is in database
            c.execute("SELECT * FROM sessions WHERE id=:id", {"id": session_id})
            result = c.fetchone()
            # return None if session is not in database
            if result:
                # create session instance from database entry and map args
                env = SessionEnvironment.from_database(session_id, bot)
                session_instance = cls(bot, result[1], result[2], result[3], result[4], result[5], env,
                                       category_id=result[0],
                                       config=SessionConfig(mute_admins=result[6], mute_members=result[7]))
                return session_instance

    def create_db_entry(self):
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM sessions WHERE id=:id", {"id": self.id})
            result = c.fetchone()
            # check if session already exists
            if not result:
                c.execute("""INSERT INTO sessions VALUES (
                             :id, :name, :guild_id, :info_channel_id, :lobby_channel_id,
                             :work_time, :break_time, :repetitions, :cfg_mute_admins
                         )""",    {"id": self.id,
                                   "name": self.name,
                                   "guild_id": self.guild_id,
                                   "info_channel_id": self.env.info_channel.id,
                                   "lobby_channel_id": self.env.lobby_channel.id,
                                   "work_time": self.timer.work_time,
                                   "break_time": self.timer.break_time,
                                   "repetitions": self.timer.repetitions,
                                   "cfg_mute_admins": self.config.mute_admins})
            conn.commit()

    @property
    def dojo(self):
        return self.bot.dojos[self.guild_id]

    #############
    #   START   #
    #############

    async def start_session(self):
        # start session timer
        asyncio.create_task(self.timer.start_timer())
        # start auto reset task
        if not self.reset_if_empty.is_running():
            self.reset_if_empty.start()
        else:
            self.reset_if_empty.restart()
        # Logging
        print("Session STARTED - with", self.member_count, "members on guild:", self.dojo.guild.name)

    ##################
    #   NAVIGATION   #
    ##################

    async def next_session(self):
        asyncio.create_task(self.update_info_embed())
        # hide start button
        start_ow = {self.env.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        await self.env.start_channel.edit(overwites=start_ow)
        # show work_channel
        work_ow = {self.env.guild.default_role: discord.PermissionOverwrite(view_channel=True)}
        await self.env.work_channel.edit(overwrites=work_ow)
        # move all members to work_channel
        for member in self.env.lobby_channel.members:
            await member.move_to(self.env.work_channel)
            # admins do not get muted automatically
            if member.guild_permissions.administrator and self.dojo.mute_admins:
                await member.edit(mute=True)
        for member in self.env.work_channel.members:
            await member.move_to(self.env.work_channel)
            # admins do not get muted automatically
            if member.guild_permissions.administrator and self.dojo.mute_admins:
                await member.edit(mute=True)
        for member in self.env.start_channel.members:
            await member.move_to(self.env.work_channel)
            # admins do not get muted automatically
            if member.guild_permissions.administrator and self.dojo.mute_admins:
                await member.edit(mute=True)
        # rename session
        session_label = f"Session [ {self.timer.session_count} | {self.timer.repetitions} ]"
        await self.env.work_channel.edit(name=session_label)

    async def take_a_break(self):
        # move members to lobby and unmute admins
        label = self.env.break_label
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
        # Logging
        print("Session RESET - ", self.member_count, " members - ", self.dojo.guild.name)
        # resets
        self.timer.reset()
        self.reset_if_empty.stop()
        await self.reset_members_and_work_channel(self.env.start_label)
        # delete timer msg
        if self.env.info_msg:
            await self.env.info_msg.delete()
            self.env.info_msg = None
        # clear info_channel
        async for msg in self.env.info_channel.history():
            if msg == self.env.info_msg:
                continue
            else:
                await msg.delete()
        # edit/create info embed
        info_embed = self.get_info_embed()
        if self.env.info_msg:
            await self.env.info_msg.edit(embed=info_embed)
        else:
            self.env.info_msg = await self.env.info_channel.send(embed=info_embed)

    ###############
    #    TOOLS    #
    ###############

    @property
    def member_count(self) -> int:
        if self.env.lobby_channel and self.env.work_channel:
            return len(self.env.lobby_channel.members) + len(self.env.work_channel.members)
        else:
            return 0

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
        for member in self.env.work_channel.members:
            await member.move_to(self.env.lobby_channel)
            # admins do not get unmuted automatically
            if member.guild_permissions.administrator:
                await member.edit(mute=False)
        # only relevant if admin leaves the session early
        for member in self.env.lobby_channel.members:
            if member.guild_permissions.administrator:
                await member.edit(mute=False)
        # reset work_channel
        if self.env.work_channel:
            await self.env.work_channel.delete()
        work_ow = {
            self.dojo.guild.me: discord.PermissionOverwrite(connect=True),
            self.dojo.guild.default_role: discord.PermissionOverwrite(speak=not self.config.mute_members)
        }
        self.env.work_channel = await self.dojo.guild.create_voice_channel(
            work_channel_label,
            category=self.env.category,
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
        await self.env.info_msg.edit(embed=info_embed)

    async def update_edit(self):
        if self.env.category.name != self.name:
            await self.env.category.edit(name=self.name)
        await self.update_info_embed()
        # update config todo
        # await self.config_msg.edit(f"Session config: {self.to_json()}")

    async def dispose(self):
        # todo env.dispose() different to session.dispose()
        # turn timer off
        self.timer.is_active = False
        # delete channels
        for vc in self.env.category.voice_channels:
            await vc.delete()
        for tc in self.env.category.text_channels:
            await tc.delete()
        del self.dojo.sessions[self.id]
        await self.env.category.delete()

    def __eq__(self, other):
        return self.id == other.id
