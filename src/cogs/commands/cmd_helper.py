import asyncio

import discord


async def feedback(context, title: str, feedback_str: str = "", seconds_until_dispose: int = 5):
    """ feedback in response to commands, both messages will automatically get removed """
    embed_msg = discord.Embed(title=title)
    if feedback_str != "":
        embed_msg.description = feedback_str
    # send feedback message
    feedback_msg = await context.send(embed=embed_msg)
    # sleep until feedback gets removed again
    await asyncio.sleep(seconds_until_dispose)
    if context.message:
        asyncio.create_task(context.message.delete())
    asyncio.create_task(feedback_msg.delete())
