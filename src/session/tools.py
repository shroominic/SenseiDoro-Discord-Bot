
async def get_session(some_channel, bot):
    # get dojo reference
    dojo = bot.dojos[some_channel.guild.id]
    if some_channel.category.id in dojo.sessions:
        return dojo.sessions[some_channel.category.id]
    elif len(dojo.sessions) == 1:
        return list(dojo.sessions.values())[0]
    else:
        return None

