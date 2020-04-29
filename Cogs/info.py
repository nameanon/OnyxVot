import discord
from discord.ext import commands
import sys
import datetime
import psutil
import os


def timeStringHandler(count):
    total_s = count.seconds
    hou, rem = divmod(total_s, 3600)
    minutes, sec = divmod(rem, 60)

    return [hou, minutes, sec]


class InfoCog(commands.Cog, name="info"):

    def __init__(self, bot):
        self.bot = bot
        self.startup_time = datetime.datetime.now()

    @commands.command(aliases=["s"])  # Ping command
    async def status(self, ctx):
        """
        Displays Running Information
        """

        ping = round((round(self.bot.latency, 3) * 1000))
        desc = f"```\nPlatform - {sys.platform}\n" \
               f"Python - {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}\n" \
               f"Discord - {discord.__version__}```"

        uptime = timeStringHandler(datetime.datetime.now() - self.startup_time)

        e = discord.Embed(title="Current Status:",
                          description=desc,
                          colour=1741991)

        e.add_field(name="Ping",
                    value=f"{ping} ms",
                    inline=True)

        e.add_field(name="Uptime:",
                    value=f"> {uptime[0]:02d}:{uptime[1]:02d}:{uptime[2]:02d}",
                    inline=True)

        #  TODO: Improve the string handler of uptime

        used_m = round(psutil.virtual_memory().used / 1024 / 1024)
        total_m = round(psutil.virtual_memory().total / 1024 / 1024)
        percent_m = round((used_m / total_m) * 100)

        e.add_field(name="MemoryUsage",
                    value=f"{used_m}/{total_m} MB \nUsing: {percent_m}%",
                    inline=False)

        await ctx.send(embed=e)

    @commands.command(aliases=["pur"])  # Deletes msgs if has perms
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=9):
        await ctx.channel.purge(limit=amount + 1)

    @commands.Cog.listener()  # Cogs listener are events in cogs
    async def on_command_error(self, ctx, error):
        await ctx.channel.send(error)

    @commands.group(name="debug", invoke_without_command=True)
    async def debug(self, ctx):
        pass

    @debug.command(aliases=["ap"])
    async def absolute_path(self, ctx):
        await ctx.send(f"{os.path.abspath(__file__)}")


def setup(bot):
    bot.add_cog(InfoCog(bot))
    print("InfoCog has been loaded")
