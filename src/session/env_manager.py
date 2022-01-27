
async def create_environment(is_new_session, session):
    if is_new_session:
        await create_new_environment(session)
    else:
        await create_from_old_environment(session)


async def create_new_environment(session):
    guild = session.dojo.guild
    # create session category
    session.category_pointer = await guild.create_category_channel(session.label)
    # create initial channels
    session.lobby_channel_pointer = await guild.create_voice_channel(
        session.lobby_label,
        category=session.category_pointer
    )
    session.work_channel_pointer = await guild.create_voice_channel(
        session.start_button_label,
        category=session.category_pointer
    )
    session.info_channel_pointer = await guild.create_text_channel(
        session.information_label,
        category=session.category_pointer
    )
    session.chat_channel_pointer = await guild.create_text_channel(
        session.chat_label,
        category=session.category_pointer
    )
    session.config_channel_pointer = await guild.create_text_channel(
        session.config_label,
        category=session.category_pointer
    )
    # set permissions
    await session.config_channel_pointer.set_permissions(guild.me, read_messages=True)
    await session.info_channel_pointer.set_permissions(guild.me, send_messages=True)
    await session.config_channel_pointer.set_permissions(guild.default_role, read_messages=False)
    await session.info_channel_pointer.set_permissions(guild.default_role, send_messages=False)
    # send serialization of session as message
    await session.config_channel_pointer.send(f"Session config: {session.to_json()}")


async def create_from_old_environment(session):
    # catch voice_channels
    for vc in session.category_pointer.voice_channels:
        channel_name = vc.name
        if session.lobby_label in channel_name:
            session.lobby_channel_pointer = vc
        if session.start_button_label in channel_name \
                or "Session" in channel_name \
                or session.session_break_label in channel_name:
            session.work_channel_pointer = vc
    # catch text_channels
    for tc in session.category_pointer.text_channels:
        channel_name = tc.name
        if session.chat_label in channel_name:
            session.chat_channel_pointer = tc
        if session.information_label in channel_name:
            session.info_channel_pointer = tc
        if session.config_label in channel_name:
            session.config_channel_pointer = tc
    # catch msg references
    async for msg in session.info_channel_pointer.history():
        if msg.embeds:
            for embed in msg.embeds:
                if "info" in embed.title:
                    session.info_msg_embed = msg
                if "timer" in embed.title:
                    session.timer.timer_info_pointer = msg
    # session reset
    await session.reset_session()
