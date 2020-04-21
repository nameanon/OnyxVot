import discord
from discord.ext import commands

class TimeCog(commands.Cog, name="time"):

    def __init__(self,bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(TimeCog(bot))
    print("TimeCog has been loaded")