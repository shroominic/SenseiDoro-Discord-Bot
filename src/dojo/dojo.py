import sqlite3
from contextlib import closing


class Dojo:
    def __init__(self, guild, bot, **kwargs):
        # references
        self.guild = guild
        self.bot = bot
        # session instances
        self.active_sessions = {}
        # button listener ids
        self.lobby_ids = []
        # role ids
        self.admin_role_id: int = kwargs.get("admin_role_id", None)
        self.moderator_role_id: int = kwargs.get("mod_role_id", None)
        # configuration
        self.mute_admins = kwargs.get("mute_admins", True)
        self.session_limit = kwargs.get("session_limit", 3)

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

    @property
    def active_users(self):
        return sum([session.member_count for session in self.active_sessions.values()])

    async def dispose(self):
        # delete all session environments
        for session in self.active_sessions.values():
            await session.dispose()
        # delete the database entry and leave the guild
        await self.guild.leave()

    async def reset_data(self):
        # delete data
        with closing(sqlite3.connect("src/dbm/sensei.db")) as conn:
            c = conn.cursor()
            # search in db for guild.id
            c.execute(" DELETE FROM dojos WHERE id=:id", {"id": self.guild.id})
            c.execute("INSERT INTO dojos VALUES (:id, :name, NULL, NULL, :cfg_mute_admins)",
                      {"id": self.guild.id,
                       "name": self.guild.name,
                       "cfg_mute_admins": self.mute_admins})
            conn.commit()
        # console info
        print(f"Guild data reset : {self.guild.name}")
