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

    def add_bot_commands_formatting(self, commands, heading):
        """Adds the minified bot heading with commands to the output.

        The formatting should be added to the :attr:`paginator`.

        The default implementation is a bold underline heading followed
        by commands separated by an EN SPACE (U+2002) in the next line.

        Parameters
        -----------
        commands: Sequence[:class:`Command`]
            A list of commands that belong to the heading.
        heading: :class:`str`
            The heading to add to the line.
        """
        if commands:
            # U+2002 Middle Dot
            joined = '\u2002'.join(c.name for c in commands)
            self.paginator.add_line('__**%s**__' % heading)
            self.paginator.add_line(joined)

    #
    #
    #

    def add_subcommand_formatting(self, command):
        """Adds formatting information on a subcommand.

        The formatting should be added to the :attr:`paginator`.

        The default implementation is the prefix and the :attr:`Command.qualified_name`
        optionally followed by an En dash and the command's :attr:`Command.short_doc`.

        Parameters
        -----------
        command: :class:`Command`
            The command to show information of.
        """
        fmt = '{0}{1} \N{EN DASH} {2}' if command.short_doc else '{0}{1}'
        self.paginator.add_line(fmt.format(self.clean_prefix, command.qualified_name, command.short_doc))

    #
    #
    #

    def add_aliases_formatting(self, aliases):
        """Adds the formatting information on a command's aliases.

        The formatting should be added to the :attr:`paginator`.

        The default implementation is the :attr:`aliases_heading` bolded
        followed by a comma separated list of aliases.

        This is not called if there are no aliases to format.

        Parameters
        -----------
        aliases: Sequence[:class:`str`]
            A list of aliases to format.
        """
        self.paginator.add_line('**%s** %s' % (self.aliases_heading, ', '.join(aliases)), empty=True)

    #
    #
    #

    def add_command_formatting(self, command):
        """A utility function to format commands and groups.

        Parameters
        ------------
        command: :class:`Command`
            The command to format.
        """

        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)

        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

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
        self.paginator.clear()
        await super().prepare_help_command(ctx, command)

    #
    #
    #

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        note = self.get_opening_note()

        if note:
            hel_e = discord.Embed(title="Help Command", description=note, colour=1741991)
            self._embed_pages.append(hel_e)

        no_category = '\u200b{0.no_category}'.format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, commands in to_iterate:
            commands = sorted(commands, key=lambda c: c.name) if self.sort_commands else list(commands)
            joined = ''.join(f"> `!{c.name}`\n" for c in commands)

            if category == "HelpCommand":
                pass
            else:
                self._embed_pages[0].add_field(name=category, value=joined)


        note = self.get_ending_note()
        if note:
            self._embed_pages.append(discord.Embed(title="", description=note))

        self._embed_pages[0].set_thumbnail(url=f"{ctx.me.avatar_url}")

        await self.send_pages(True)


    #
    #
    #

    # async def send_cog_help(self, cog):
    #     bot = self.context.bot
    #     coh_help_e = discord.Embed(title=f"{cog} Help")
    #     if bot.description:
    #         coh_help_e.description = bot.description
    #
    #     note = self.get_opening_note()
    #     if note:
    #         coh_help_e.description += "\n" + note
    #
    #     if cog.description:
    #         coh_help_e.description += "\n" + note
    #
    #     filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
    #     if filtered:
    #         self.paginator.add_line('**%s %s**' % (cog.qualified_name, self.commands_heading))
    #         for command in filtered:
    #             self.add_subcommand_formatting(command)
    #
    #         note = self.get_ending_note()
    #         if note:
    #             self.paginator.add_line()
    #             self.paginator.add_line(note)
    #
    #     await self.send_pages()

    #
    #
    #

    async def send_group_help(self, group):
        self.add_command_formatting(group)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        if filtered:
            note = self.get_opening_note()
            if note:
                self.paginator.add_line(note, empty=True)

            self.paginator.add_line('**%s**' % self.commands_heading)
            for command in filtered:
                self.add_subcommand_formatting(command)

            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

        await self.send_pages()

    #
    #
    #

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages()

