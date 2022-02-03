
class Dojo:
    def __init__(self, guild, bot, session_limit=2):
        # references
        self.guild = guild
        self.bot = bot
        self.session_limit = session_limit
        self.sessions = {}
        # config
        self.config_channel = None
        self.config_msg = None
        # roles
        self.admin_role = None
        self.moderator_role = None
        # configuration
        self.mute_admins = True

    async def update_config(self):
        if not self.config_msg or not self.config_channel:
            if not self.config_channel:
                pass
