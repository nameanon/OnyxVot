import discord
from discord.ext import commands
from .EmbedHelpCommand import EmbedHelpCommand

class HelpCommand(commands.Cog, name="HelpCommand"):

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = EmbedHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(HelpCommand(bot))
    print("HelpCommand has been loaded")
