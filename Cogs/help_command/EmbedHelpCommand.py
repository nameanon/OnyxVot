from discord.ext import commands


class EmbedHelpCommand(commands.MinimalHelpCommand):

    def get_command_signature(self, command):
        return f'{self.clean_prefix}{command.qualified_name} {command.signature}'
