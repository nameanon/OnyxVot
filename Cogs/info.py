import discord
from discord.ext import commands
import sys
import datetime


def timeStringHandler(count):

    totalS = count.seconds
    hou, rem = divmod(totalS, 3600)
    minut, sec = divmod(rem, 60)

    return [hou, minut, sec]


class InfoCog(commands.Cog, name="info"):

    def __init__(self, bot):
        self.bot = bot
        self.starupTime = datetime.datetime.now()


    @commands.command(aliases = ["s"])  # Ping command
    async def status(self, ctx):
        """
        Displays Running Infomration
        """



        ping = round((round(self.bot.latency, 3) * 1000))
        desc = f"```\nPlatform - {sys.platform}\n" \
               f"Python - {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}\n" \
               f"Discord - {discord.__version__}```"

        uptime = timeStringHandler(datetime.datetime.now() - self.starupTime)

        e = discord.Embed(title="Current Status:",
                          description=desc,
                          colour=1741991)

        e.add_field(name="Ping",
                    value=f"{ping} ms",
                    inline=True)
        e.add_field(name="Uptime:",
                    value=f"> {uptime[0]:02d}:{uptime[1]:02d}:{uptime[2]:02d}",
                    inline=True)

        await ctx.send(embed=e)


    @commands.command(aliases = ["pur"])  # Deletes msgs if has perms
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=10):
        await ctx.channel.purge(limit=amount)


    @commands.Cog.listener()  # Cogs listener are events in cogs
    async def on_command_error(self, ctx, error):
        await ctx.channel.send(error)


def setup(bot):
    bot.add_cog(InfoCog(bot))
    print("InfoCog has been loaded")
