import json

from models.session import Session


async def get_session(some_channel, bot):
    for channel in some_channel.category.text_channels:
        if channel.name == Session.config_label:
            async for msg in channel.history():
                if "Session config:" in msg.content:
                    if msg.author == bot.user and msg.content.startswith('Session config:'):
                        # parse string representation of json
                        config_json = str(msg.content)[15::]
                        config = json.loads(config_json)
                        return list(filter(lambda x: x.id == config["id"], bot.sessions))[0]