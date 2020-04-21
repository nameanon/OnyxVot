import discord
from discord.ext import commands
import time

class TimeCog(commands.Cog, name="time"):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def time(self,ctx):
        ctx.send(time.CLOCK_REALTIME)



def setup(bot):
    bot.add_cog(TimeCog(bot))
    print("TimeCog has been loaded")