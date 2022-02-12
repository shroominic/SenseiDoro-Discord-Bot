import asyncio

import discord


async def response(context, title: str, description: str = "", seconds_until_dispose: int = 10):
    """ feedback in response to commands, both messages will automatically get removed """
    embed_msg = discord.Embed(title=title)
    if description != "":
        embed_msg.description = description
    # send feedback message
    await context.respond(embed=embed_msg)
    # sleep until feedback gets removed again
    await asyncio.sleep(seconds_until_dispose)
    if context:
        asyncio.create_task(context.delete())
