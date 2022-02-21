import asyncio

import discord


# slash response
async def _slash_response(context, title: str, description: str, seconds_until_dispose: int):
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


def slash_response(context, title: str, description: str = "", seconds_until_dispose: int = 10):
    """ async task wrapper for slash_response """
    asyncio.create_task(_slash_response(context, title, description, seconds_until_dispose))


# response
async def _response(context, title: str, description: str, seconds_until_dispose: int):
    """ feedback in response to commands, both messages will automatically get removed """
    embed_msg = discord.Embed(title=title)
    if description != "":
        embed_msg.description = description
    # send feedback message
    await context.send(embed=embed_msg)
    # sleep until feedback gets removed again
    await asyncio.sleep(seconds_until_dispose)
    if context:
        asyncio.create_task(context.delete())


def response(context, title: str, description: str = "", seconds_until_dispose: int = 10):
    """ async task wrapper for response """
    asyncio.create_task(_response(context, title, description, seconds_until_dispose))


