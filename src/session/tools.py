
async def get_session(some_channel, bot):
    # get dojo reference
    dojo = bot.dojos[some_channel.guild.id]
    session = dojo.sessions[some_channel.category.id]
    return session
