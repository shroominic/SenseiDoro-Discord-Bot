import asyncio
import functools

from src.cogs.better_response import slash_response


def default_feedback(title, description="", seconds_visible=10):
    def _default_feedback(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # function application
            result = await func(*args, **kwargs)
            # feedback
            ctx = args[1]
            asyncio.create_task(slash_response(ctx, title, description, seconds_visible))
            # func return
            return result
        return wrapper
    return _default_feedback


def admin_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        self = args[0]
        ctx = args[1]
        # only with admin role
        dojo = self.bot.dojos[ctx.guild.id]
        role = dojo.admin_role
        # if user has the role
        if role in ctx.author.roles:
            # function application
            return await func(*args, **kwargs)
        # if role not set
        elif not role:
            title = "Admin role not set"
            feedback = "Type `/role admin @YOUR_ADMIN_ROLE` to use this command."
            asyncio.create_task(slash_response(ctx, title, feedback))
        else:
            title = "Missing Role"
            feedback = f"Only user with @{role.name} can run this command."
            asyncio.create_task(slash_response(ctx, title, feedback))
    return wrapper


def mod_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        self = args[0]
        ctx = args[1]
        # only with mod role
        dojo = self.bot.dojos[ctx.guild.id]
        role = dojo.mod_role
        # if user has the role
        if role in ctx.author.roles:
            # function application
            return await func(*args, **kwargs)
        # if role not set
        elif not role:
            title = "Moderator role not set"
            feedback = "Type `/role moderator @YOUR_MOD_ROLE` to use this command."
            asyncio.create_task(slash_response(ctx, title, feedback))
        else:
            title = "Missing Role"
            feedback = f"Only user with @{role.name} can run this command."
            asyncio.create_task(slash_response(ctx, title, feedback))
    return wrapper
