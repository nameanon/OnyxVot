import discord

async def schedule(dt, coro, *args, **kwargs):
    # print(f"scheduled: {dt} - {coro} - {args} - {kwargs}")
    await discord.utils.sleep_until(dt)
    return await coro(*args, **kwargs)