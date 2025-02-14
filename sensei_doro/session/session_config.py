

class SessionConfig:
    def __init__(self, **kwargs):
        self.mute_admins = kwargs.get("mute_admins", True)
        self.mute_members = kwargs.get("mute_members", True)
