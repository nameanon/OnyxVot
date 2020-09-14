import asyncio
from discord.ext import commands
from discord.ext.commands import Paginator
import discord
import itertools


class EmbedHelpCommand(commands.MinimalHelpCommand):
    """An implementation of a help command with minimal output.

    This inherits from :class:`HelpCommand`.

    Attributes
    ------------
    sort_commands: :class:`bool`
        Whether to sort the commands in the output alphabetically. Defaults to ``True``.
    commands_heading: :class:`str`
        The command list's heading string used when the help command is invoked with a category name.
        Useful for i18n. Defaults to ``"Commands"``
    aliases_heading: :class:`str`
        The alias list's heading string used to list the aliases of the command. Useful for i18n.
        Defaults to ``"Aliases:"``.
    dm_help: Optional[:class:`bool`]
        A tribool that indicates if the help command should DM the user instead of
        sending it to the channel it received it from. If the boolean is set to
        ``True``, then all help output is DM'd. If ``False``, none of the help
        output is DM'd. If ``None``, then the bot will only DM when the help
        message becomes too long (dictated by more than :attr:`dm_help_threshold` characters).
        Defaults to ``False``.
    dm_help_threshold: Optional[:class:`int`]
        The number of characters the paginator must accumulate before getting DM'd to the
        user if :attr:`dm_help` is set to ``None``. Defaults to 1000.
    no_category: :class:`str`
        The string used when there is a command which does not belong to any category(cog).
        Useful for i18n. Defaults to ``"No Category"``
    paginator: :class:`Paginator`
        The paginator used to paginate the help command output.
    """

    def __init__(self, **options):
        self._embed_pages = []
        self.current_page = 0
        self.embed_colour = 1741991

        super().__init__(**options)

    #
    #
    #

    async def send_pages(self, embed=False):
        """A helper utility to send the page output from :attr:`paginator` to the destination."""
        destination = self.get_destination()
        if embed:
            for page in self._embed_pages:
                await destination.send(embed=page)
        else:
            for page in self.paginator.pages:
                await destination.send(page)


    #
    #
    #

    def get_opening_note(self):
        """Returns help command's opening note. This is mainly useful to override for i18n purposes.

        The default implementation returns ::

            Use `{prefix}{command_name} [command]` for more info on a command.
            You can also use `{prefix}{command_name} [category]` for more info on a category.

        """
        command_name = self.invoked_with
        return "Use `{0}{1} [command]` for more info on a command.\n" \
               "You can also use `{0}{1} [category]` for more info on a category.".format(self.clean_prefix, command_name)

    #
    #
    #

    def get_command_signature(self, command):
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    #
    #
    #

    def get_ending_note(self):
        """Return the help command's ending note. This is mainly useful to override for i18n purposes.

        The default implementation does nothing.
        """
        return None

    #
    #
    #

    #
    #
    #

    #
    #
    #

    #
    #
    #

    def get_destination(self):
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        elif self.dm_help is None and len(self.paginator) > self.dm_help_threshold:
            return ctx.author
        else:
            return ctx.channel

    #
    #
    #

    async def prepare_help_command(self, ctx, command):
        del self._embed_pages
        self._embed_pages = []
        await super().prepare_help_command(ctx, command)

    #
    #
    #

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        hel_e = discord.Embed(title="Help Command", description="", colour=self.embed_colour)

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        note = self.get_opening_note()

        if note:
            hel_e.description = note

        no_category = '\u200b{0.no_category}'.format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, commands in to_iterate:
            commands = sorted(commands, key=lambda c: c.name) if self.sort_commands else list(commands)
            joined = ''.join(f"> `{self.clean_prefix}{c.name}`\n" for c in commands)

            if category == "HelpCommand":
                pass
            else:
                hel_e.add_field(name=category, value=joined)


        note = self.get_ending_note()
        if note:
            self._embed_pages.append(discord.Embed(title="", description=note))

        hel_e.set_thumbnail(url=f"{ctx.me.avatar_url}")

        self._embed_pages.append(hel_e)
        await self.send_pages(True)


    #
    #
    #

    async def send_cog_help(self, cog):
        bot = self.context.bot
        cog_help_e = discord.Embed(title=f"", description="", colour=self.embed_colour)

        if bot.description:
            cog_help_e.description = bot.description

        note = self.get_opening_note()
        if note:
            cog_help_e.description = cog_help_e.description + "\n" + note

        if cog.description:
            cog_help_e.description = cog_help_e.description + "\n" + cog.description

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)

        if filtered:
            cog_help_e.title = cog.qualified_name

            commands_text = ""

            for command in filtered:
                if command.signature:
                    commands_text = commands_text + f"> `{self.clean_prefix}{command.qualified_name} {command.signature}` - {command.short_doc}\n"
                else:
                    commands_text = commands_text + f"> `{self.clean_prefix}{command.qualified_name}` - {command.short_doc}\n"

            cog_help_e.add_field(name="Commands: ", value=commands_text)

            note = self.get_ending_note()

            if note:
                cog_help_e.add_field(name="", value=note)

        cog_help_e.set_thumbnail(url=f"{self.context.me.avatar_url}")

        self._embed_pages.append(cog_help_e)

        await self.send_pages(True)

    #
    #
    #

    async def send_group_help(self, group):
        bot = self.context.bot
        group_help_e = discord.Embed(title=f"", description="", colour=self.embed_colour)

        if bot.description:
            group_help_e.description = bot.description

        note = self.get_opening_note()
        if note:
            group_help_e.description = group_help_e.description + "\n" + note

        if group.description:
            group_help_e.description = group_help_e.description + "\n" + group.description

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)

        if filtered:
            group_help_e.title = group.name

            commands_text = ""

            for command in filtered:
                if command.signature:
                    commands_text = commands_text + f"> `{self.clean_prefix}{command.qualified_name} {command.signature}` - {command.short_doc}\n"
                else:
                    commands_text = commands_text + f"> `{self.clean_prefix}{command.qualified_name}` - {command.short_doc}\n"

            group_help_e.add_field(name="Commands: ", value=commands_text)

            note = self.get_ending_note()

            if note:
                group_help_e.add_field(name="", value=note)

        group_help_e.set_thumbnail(url=f"{self.context.me.avatar_url}")

        self._embed_pages.append(group_help_e)

        await self.send_pages(True)




    #
    #
    #

    async def send_command_help(self, command):
        com_help = discord.Embed(title=f"{self.clean_prefix}{command.qualified_name} {command.signature}")
        com_help.colour = self.embed_colour
        if command.description:
            com_help.description = command.description
        elif command.short_doc:
            com_help.description = command.short_doc
        com_help.set_thumbnail(url=f"{self.context.me.avatar_url}")
        self._embed_pages.append(com_help)
        await self.send_pages(True)

