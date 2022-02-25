import asyncio
import json

from src.session import Session


class Dojo:
    def __init__(self, guild, bot, **kwargs):
        # references
        self.guild = guild
        self.bot = bot
        self.sessions = {}
        # roles
        self.admin_role_id: int = kwargs.get("admin_role_id", None)
        self.moderator_role_id: int = kwargs.get("mod_role_id", None)
        # configuration
        self.mute_admins = kwargs.get("mute_admins", True)
        self.session_limit = kwargs.get("session_limit", 2)
        # async init
        asyncio.create_task(self.serialize_sessions())

    @classmethod
    def new_db_entry(cls, guild, bot, db_cursor):
        new_cls = cls(guild, bot)
        db_cursor.execute("INSERT INTO dojos VALUES (:id, :name, NULL, NULL, :cfg_mute_admins)",
                          {"id": guild.id,
                           "name": guild.name,
                           "cfg_mute_admins": new_cls.mute_admins})
        return new_cls

    @classmethod
    def from_db(cls, guild, bot, admin_role_id: int, mod_role_id: int, mute_admins: bool):
        return cls(guild, bot,
                   admin_role_id=admin_role_id,
                   mod_role_id=mod_role_id,
                   mute_admins=mute_admins)

    @property
    def admin_role(self):
        if self.admin_role_id:
            return self.guild.get_role(int(self.admin_role_id))

    @property
    def mod_role(self):
        if self.moderator_role_id:
            return self.guild.get_role(int(self.moderator_role_id))
        return self.guild.default_role

    async def serialize_sessions(self):
        """ Searches for all pomodoro sessions on the server
            to reinitialize lost instances during a restart.
        """
        # serialize old session instances
        for category in self.guild.categories:
            if "🍅" in category.name:
                # find message with session config
                for tc in category.text_channels:
                    if tc is not None:
                        if tc.name == Session.config_label:
                            async for msg in tc.history():
                                if msg.author == self.bot.user and msg.content.startswith('Session config:'):
                                    # parse string representation of json
                                    config_json = str(msg.content)[15::]
                                    config = json.loads(config_json)
                                    # create session instance from json
                                    Session(
                                        dojo=self,
                                        category=category,
                                        work_time=config["work_time"],
                                        break_time=config["pause_time"],
                                        repetitions=config["number_sessions"],
                                        session_name=config["name"],
                                        is_new_session=False)
