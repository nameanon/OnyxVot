import discord
from discord.ext import commands


class InfoCog(commands.Cog, name="info"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command() #Ping command
    async def ping(self, ctx):
        ping = int (round(self.bot.latency, 3) * 1000)
        await ctx.send(f"Pong {ping} ms!")

    @commands.command() #Deletes msgs if has perms
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=10):
        await ctx.channel.purge(limit=amount)

    @commands.Cog.listener() # Cogs listener are events in cogs
    async def on_command_error(self, ctx, error):
        await ctx.channel.send(error)






def setup(bot):
    bot.add_cog(InfoCog(bot))
    print("InfoCog has been loaded")
