

async def create_new_environment(session):
    # create session category
    session.category_pointer = await session.guild_pointer.create_category_channel(session.name)
    # create initial channels
    session.chat_channel_pointer = await session.guild_pointer.create_text_channel(
        session.chat_label,
        category=session.category_pointer
    )
    session.lobby_channel_pointer = await session.guild_pointer.create_voice_channel(
        session.lobby_label,
        category=session.category_pointer
    )
    session.work_channel_pointer = await session.guild_pointer.create_voice_channel(
        session.start_button_label,
        category=session.category_pointer
    )
    session.info_channel_pointer = await session.guild_pointer.create_text_channel(
        session.information_label,
        category=session.category_pointer
    )

    session.config_channel_pointer = await session.guild_pointer.create_text_channel(
        session.config_label,
        category=session.category_pointer
    )
    # set permissions
    await session.config_channel_pointer.set_permissions(session.guild_pointer.default_role, read_messages=False)
    await session.info_channel_pointer.set_permissions(session.guild_pointer.default_role, write_messages=False)
    # send serialization of models as message
    await session.config_channel_pointer.send(f"Session config: {session.to_json()}")


async def create_from_old_environment(session):
    for vc in session.category_pointer.voice_channels:
        channel_name = vc.name
        if session.lobby_label in channel_name:
            session.lobby_channel_pointer = vc
        if session.start_button_label in channel_name \
                or "Session" in channel_name \
                or session.session_break_label in channel_name:
            session.work_channel_pointer = vc
    for tc in session.category_pointer.text_channels:
        channel_name = tc.name
        if session.chat_label in channel_name:
            session.chat_channel_pointer = tc
    await session.reset_session()