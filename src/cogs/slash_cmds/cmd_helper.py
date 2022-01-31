import asyncio

import discord


async def feedback(context, title: str, feedback_str: str = "", seconds_until_dispose: int = 10):
    """ feedback in response to commands, both messages will automatically get removed """
    embed_msg = discord.Embed(title=title)
    if feedback_str != "":
        embed_msg.description = feedback_str
    # send feedback message
    await context.respond(embed=embed_msg)
    # sleep until feedback gets removed again
    await asyncio.sleep(seconds_until_dispose)
    asyncio.create_task(context.delete())
