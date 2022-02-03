import asyncio

from discord.utils import get


class Dojo:
    def __init__(self, guild, bot, session_limit=2):
        # references
        self.guild = guild
        self.bot = bot
        self.session_limit = session_limit
        self.sessions = {}
        # roles
        self.admin_role = None
        self.moderator_role = None
        # configuration
        self.mute_admins = True
