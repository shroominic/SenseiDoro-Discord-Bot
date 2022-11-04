import json
import sqlite3
from abc import ABC
from contextlib import closing

import discord
from discord.ext import commands
from discord import Embed


# Bot Client Class
class SenseiClient(commands.AutoShardedBot, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # stores all dojos of connected guilds
        self.dojos = {}
        self.topgg = None
        self.log = None

    def get_dojo(self, guild_id):
        return self.dojos.get(guild_id, None)

    async def migration(self):
        """ run the bot """
        sessions_to_migrate = []
        self.log.send_log("Collecting sessions to migrate...", delete_after=5)
        # search for dojos to migrate
        for dojo in self.dojos.values():
            # search for categories with "🍅" in the name or with config channel (+ cfg msg)
            for category in dojo.guild.categories:
                if "🍅" in category.name or "Pomodoro" in category.name:
                    # find message with session config
                    try:
                        for tc in category.text_channels:
                            if tc is not None:
                                if tc.name == "config":
                                    async for msg in tc.history():
                                        if msg.author == self.user and msg.content.startswith('Session config:'):
                                            # parse string representation of json
                                            config_json = str(msg.content)[15::]
                                            session_config = json.loads(config_json)
                                            # add category and config channel
                                            session_config["category"] = category
                                            session_config["config_channel"] = tc
                                            # add session to list
                                            sessions_to_migrate.append(session_config)
                    except Exception as e:
                        self.log.exception(f"Failed to migrate session", e)
            # search for old text and voice channel names
            for session_dict in sessions_to_migrate:
                for tc in session_dict["category"].text_channels:
                    if tc is not None:
                        if tc.name == "chat":
                            session_dict["chat_channel"] = tc
                        elif tc.name == "info":
                            session_dict["info_channel"] = tc
                for vc in session_dict["category"].voice_channels:
                    if vc is not None:
                        if vc.name == "Lobby":
                            session_dict["lobby_channel"] = vc
                        elif vc.name == "START SESSION":
                            session_dict["start_channel"] = vc
        # list these dojos
        print(f"Found {len(sessions_to_migrate)} sessions to migrate")
        print(f"Migration started...")
        self.log.send_log(f"Found {len(self.dojos)} dojos to migrate", delete_after=5)
        self.log.send_log(f"Migration started...", delete_after=15)
        # migrate... (todo check for permissions)
        global migration_msg_instance
        for session_dict in sessions_to_migrate:
            # send message to all migrating sessions
            migration_msg = Embed(title="Migrate session to new version ...",
                                  description="Sensei Doro has been updated to a new version, \n"
                                              "major features include a more minimalistic design\n"
                                              "which will change this session environment.\n"
                                              "If something goes wrong, please contact me in the support server.\n"
                                              "https://discord.gg/4gZxCAK9mb")
            if c := (session_dict["info_channel"] or session_dict["chat_channel"]):
                migration_msg_instance = await c.send(embed=migration_msg)
            else:
                self.log.send_log(f"Could not send migration message to {session_dict['category'].name}"
                                  f"inside {session_dict['category'].guild.name}", delete_after=60*60)
            # migrate current session

            # delete old unused channels if they are empty if not then rename them and send info message
            if session_dict["chat_channel"] is not None:
                try:
                    await session_dict["chat_channel"].delete()
                except Exception as e:
                    self.log.exception(f"Failed to delete channel {session_dict['chat_channel'].name}", e)
            if session_dict["start_channel"] is not None:
                try:
                    await session_dict["start_channel"].delete()
                except Exception as e:
                    self.log.exception(f"Failed to delete channel {session_dict['start_channel'].name}", e)
            if session_dict["config_channel"] is not None:
                try:
                    await session_dict["config_channel"].delete()
                except Exception as e:
                    self.log.exception(f"Failed to delete channel {session_dict['config_channel'].name}", e)
            # rename still used channels and category to match new session environment
            # and create new channels if not found
            if session_dict["info_channel"] is not None:
                try:
                    await session_dict["info_channel"].edit(name="📋dashboard")
                except Exception as e:
                    self.log.exception(f"Failed to rename channel {session_dict['info_channel'].name}", e)
            else:
                info_ow = {
                    session_dict["category"].guild.self_role: discord.PermissionOverwrite(send_messages=True,
                                                                                          view_channel=True),
                    session_dict["category"].guild.default_role: discord.PermissionOverwrite(send_messages=False),
                }
                await session_dict["category"].guild.create_text_channel(name="📋dashboard",
                                                                         category=session_dict["category"],
                                                                         overwrites=info_ow)
            if session_dict["lobby_channel"]:
                try:
                    await session_dict["lobby_channel"].edit(name="☕️ lobby")
                except Exception as e:
                    self.log.exception(f"Failed to rename channel {session_dict['lobby_channel'].name}", e)
            else:
                session_dict["lobby_channel"] = await session_dict["category"].guild.create_voice_channel(
                    name="☕️ lobby",
                    category=session_dict["category"])
            # delete previous migration message
            if msg := migration_msg_instance:
                await msg.delete()
            # write migration information msg to dashboard channel
            if c := (session_dict["info_channel"] or session_dict["lobby_channel"]):
                # tell users that the session has been migrated
                embed = discord.Embed(title="Session updated!",
                                      description="This session has been updated to the new version of Sensei Doro.\n"
                                                  "If you have any questions, problems or feedback, \n"
                                                  "please contact me [here](https://discord.gg/4gZxCAK9mb) :)")
                await c.send(embed=embed)
            # and if everything went fine
            # create db entry for new session
            with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM sessions WHERE id=:id", {"id": session_dict["category"].id})
                result = c.fetchone()
                if not result:
                    c.execute("""INSERT INTO sessions VALUES (
                                 :id, :name, :guild_id, :info_channel_id, :lobby_channel_id,
                                 :work_time, :break_time, :repetitions, :cfg_mute_admins
                             )""", {"id": session_dict["category"].id,
                                    "name": session_dict["category"].name,
                                    "guild_id": session_dict["category"].guild.id,
                                    "info_channel_id": session_dict["info_channel"].id,
                                    "lobby_channel_id": session_dict["lobby_channel"].id,
                                    "work_time": (time if (time := session_dict["work_time"]) else 25),
                                    "break_time": (time if (time := session_dict["pause_time"]) else 25),
                                    "repetitions": (reps if (reps := session_dict["number_sessions"]) else 25),
                                    "cfg_mute_admins": True})
                conn.commit()
            # register lobby_id to dojo instance
            dojo = self.get_dojo(session_dict["category"].guild.id)
            dojo.lobby_ids.append(session_dict["lobby_channel"].id)
            # log migrated session
            self.log.send_log(f"Session {session_dict['category'].name} successfully migrated.")
        # send migration finished message
        self.log.send_log(f"Migration finished!", delete_after=15)

    async def close(self):
        """ exit the whole application safely """
        print("Shutdown Sensei Doro... ")
        # close all active sessions
        for dojo in self.dojos.values():
            for session in list(dojo.active_sessions.values()):
                try:
                    await session.close()
                    session.send_notification("🚧 Session closed due to server maintenance 🛠",
                                              "Sorry for the inconvenience, 🚁 we're back online soon!")
                except Exception as e:
                    self.log.exception(f"failed to close session", e)
        # stop all tasks
        if self.topgg:
            await self.topgg.close()
        if self.log:
            self.log.auto_refresh.stop()
        # shutdown the bot
        await super().close()
        print("Shutdown complete.")

    # statistics todo: move to different place
    @property
    def total_dojos(self):
        return len(self.dojos)

    @property
    def total_sessions(self):
        return sum([len(dojo.lobby_ids) for dojo in self.dojos.values()])

    @property
    def total_active_sessions(self):
        return sum([len(dojo.active_sessions.values()) for dojo in self.dojos.values()])

    @property
    def total_active_users(self):
        return sum([dojo.active_users for dojo in self.dojos.values()])

    @property
    def total_sessions_24h(self):
        return 0  # todo

    @property
    def total_users_24h(self):
        # todo
        return 0  # todo
