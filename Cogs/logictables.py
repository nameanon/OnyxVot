import discord
from discord.ext import commands

class LogicCog(commands.Cog, name="logic"):

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(LogicCog(bot))
    print("LogicCog has been loaded")