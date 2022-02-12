import asyncio

import discord


async def create_environment(is_new_session, session):
    if is_new_session:
        await create_new_environment(session)
    else:
        await create_from_old_environment(session)


async def create_new_environment(session):
    guild = session.dojo.guild
    # permission overwrites
    config_ow = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    info_ow = {
        guild.default_role: discord.PermissionOverwrite(send_messages=False),
        guild.me: discord.PermissionOverwrite(send_messages=True)
    }
    work_ow = {
        guild.default_role: discord.PermissionOverwrite(speak=False)
    }
    # create session category
    session.category_pointer = await guild.create_category_channel(session.label)
    # create initial channels
    session.lobby_channel_pointer = await guild.create_voice_channel(session.lobby_label,
                                                                     category=session.category_pointer)
    session.work_channel_pointer = await guild.create_voice_channel(session.start_button_label,
                                                                    category=session.category_pointer,
                                                                    overwrites=work_ow)
    session.info_channel_pointer = await guild.create_text_channel(session.information_label,
                                                                   category=session.category_pointer,
                                                                   overwrites=info_ow)
    session.chat_channel_pointer = await guild.create_text_channel(session.chat_label,
                                                                   category=session.category_pointer, )
    session.config_channel_pointer = await guild.create_text_channel(session.config_label,
                                                                     category=session.category_pointer,
                                                                     overwrites=config_ow)
    # send serialization of session as message
    session.config_msg = await session.config_channel_pointer.send(f"Session config: {session.to_json()}")


async def create_from_old_environment(session):
    # catch voice_channels
    for vc in session.category_pointer.voice_channels:
        channel_name = vc.name
        if session.lobby_label in channel_name:
            session.lobby_channel_pointer = vc
        if session.start_button_label in channel_name \
                or "Session" in channel_name \
                or session.break_time_label in channel_name\
                or "Take a break" in channel_name:  # TODO only temp
            session.work_channel_pointer = vc
    # catch text_channels
    for tc in session.category_pointer.text_channels:
        channel_name = tc.name
        if session.chat_label in channel_name:
            session.chat_channel_pointer = tc
        if session.information_label in channel_name\
                or "information" in channel_name:  # TODO only temp
            session.info_channel_pointer = tc
        if session.config_label in channel_name:
            session.config_channel_pointer = tc
    # changes to activ servers
    if session.info_channel_pointer.name != session.information_label:
        await session.info_channel_pointer.edit(name=session.information_label)
    # catch msg references
    async for msg in session.config_channel_pointer.history():
        if msg.author == session.dojo.bot.user and msg.content.startswith('Session config:'):
            session.config_msg = msg
    async for msg in session.info_channel_pointer.history():
        if msg.embeds:
            for embed in msg.embeds:
                if embed.fields:
                    for field in embed.fields:
                        if "session" in field.name:
                            session.info_msg_embed = msg
                if "timer" in embed.title:
                    session.timer.info_msg = msg
    # session reset
    asyncio.create_task(session.reset_session())
