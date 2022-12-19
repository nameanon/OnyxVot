import asyncio
import discord
from discord.ext import commands, tasks
from .._menus_for_list import AllListSource, UserListSource, menus
from dateutil import parser

from .db_models import *
from .schedule import schedule
from .get_datetime_obj import get_datetime_obj
from .doRemind import doRemind
import pytz


class ReminderCog2(commands.Cog, name="ReminderCog"):

    def __init__(self, bot):
        self.bot = bot

        ct = datetime.datetime.utcnow()
        self.ct = ct - datetime.timedelta(microseconds=ct.microsecond)

        self.embed_colour = 1741991
        #self.db_con = self.bot.loop.create_task(db_init("rem.db"))
        self.rem_task_init = self.bot.loop.create_task(self.rem_task_init())

        self.rem_total = None
        self.rem_past = None

        self.time_updater.start()  # Starts the time and presence updater

    #
    # Tasks
    #

    @tasks.loop(seconds=1)
    async def time_updater(self):

        ct = datetime.datetime.utcnow()
        self.ct = ct - datetime.timedelta(microseconds=ct.microsecond)
        self.ct = pytz.utc.localize(ct)

        #await asyncio.wait([self.db_con])
        await asyncio.wait([self.rem_task_init])

        if self.rem_total is None:
            self.rem_total = len(await Reminder.all().values_list("rem_id", flat=True))

        elif self.rem_total not in [self.rem_past, 0]:
            self.rem_past = self.rem_total

            ac = discord.Activity(name=f"{self.rem_total} reminders",
                                  type=discord.ActivityType.watching)

            await self.bot.change_presence(status=discord.Status.online, activity=ac)

        elif self.rem_total != self.rem_past:

            self.rem_past = self.rem_total

            ac = discord.Activity(
                name="with ideas to remind", type=discord.ActivityType.playing
            )

            await self.bot.change_presence(status=discord.Status.online, activity=ac)

    async def rem_task_init(self):
        #await asyncio.wait([self.db_con])

        async for rem in Reminder.all():

            if rem.time_due_col < self.ct:
                print(f"DELETE: {rem}")
                await rem.delete()

            else:
                self.bot.loop.create_task(schedule(rem.time_due_col, doRemind, self, rem), name=f"REMIND{rem.rem_id}")

    @tasks.loop(hours=12)
    async def db_pruner(self):
        """
        Deletes all reminders on the db that have already passed
        """

        async for rem in Reminder.all():
            if rem.time_due_col < self.ct:
                await rem.delete()

    #
    # Commands
    #

    @commands.command(aliases=["t", "ct"])
    async def current_time(self, ctx):
        """
        Sends the current time variable
        """
        await ctx.channel.send(f"{self.ct}")

    #
    # Rem Group
    #

    @commands.group(name="r", invoke_without_command=True)
    async def rem(self, ctx):
        if commands.is_owner():
            e = discord.Embed(title="Reminder Module:",
                              description="Commands supported: \n"
                                          "1.`list [in_dms_optional]` - Lists all your reminders\n"
                                          "2.`list_user [user id]`\n"
                                          "3.`list_all` - Lists all reminders on the db\n"
                                          "4.`me [description] (in | at | on) [time]`\n"
                                          "5.`prune [reminder id as shown in list]` - Deletes Reminder\n"
                                          "6.`prune_user [user_id]` (Owner Only)\n",
                              colour=self.embed_colour)

        else:
            e = discord.Embed(title="Reminder Module:",
                              description="Commands supported:\n"
                                          "1.`list [in_dms_optional]` - Lists all your reminders\n"
                                          "2.`me [description] (in | at | on) [time]`\n"
                                          "3.`prune [reminder id as shown in list]` - Deletes Reminder\n",
                              colour=self.embed_colour)

        await ctx.send(embed=e)

    #
    #
    #

    @rem.command(name="me")
    async def me(self, ctx, rem_dsc, connector, *, time_input):
        """
        Reminds you in the time specified
        """

        if connector not in ["in", "on", "at"]:
            raise commands.BadArgument("Wrong command format")

        if len(rem_dsc) > 240:
            raise commands.BadArgument("The remainders can't exceed 240 characters")

        try:
            if connector == "in":
                time_dif = get_datetime_obj(time_input)
                time_due = self.ct + time_dif

            elif connector == "on":
                time_due = parser.parse(time_input, fuzzy=True)

                if time_due < self.ct:
                    time_due += datetime.timedelta(days=360)

                time_dif = time_due - self.ct

            elif connector == "at":
                time_due = parser.parse(time_input)

                if time_due < self.ct:
                    time_due += datetime.timedelta(days=1)

                time_dif = time_due - self.ct

            assert time_due
            assert time_dif

        except ValueError:
            raise commands.BadArgument("Unknown date format")

        finally:

            rems_for_user = await Reminder.all().filter(user_bind=ctx.author.id) \
                .filter(time_due_col__gte=time_due - datetime.timedelta(minutes=30)) \
                .filter(time_due_col__lte=time_due + datetime.timedelta(minutes=30))

            if len(rems_for_user) < 10:

                r = await Reminder.create(desc=rem_dsc,
                                          time_due_col=time_due,
                                          user_bind=ctx.author.id,
                                          time_differential=time_dif)

                self.bot.loop.create_task(schedule(r.time_due_col, doRemind, self, r), name=f"REMIND{r.rem_id}")
                self.rem_total += 1

            else:
                raise commands.BadArgument("Limit for reminders in that time reached.\n"
                                           "Only 15 reminders per hour allowed")

        e = discord.Embed(title="Added:",
                          description=f"{r}",
                          colour=self.embed_colour)

        e.set_footer(text=f"ID: {r.rem_id}")

        await ctx.channel.send(embed=e)

    #
    # Error Handle for me command
    #

    @me.error
    async def me_error(self, ctx, error):

        prefix = await self.bot.get_prefix(ctx.message)
        perms = [perm for perm, value in ctx.me.permissions_in(ctx.channel) if value]

        if "embed_links" in perms:

            e_error = discord.Embed(title="Command Error")
            e_error.colour = 15158332
            e_error.description = f"Error: {error}\n" \
                                  f"Please input the command in the correct format: \n\n" \
                                  f'`{prefix}r me "<rem_description>" (in|on|at) <time>`\n' \
                                  f"Valid Time Formats -> \n" \
                                  f"> `#d#h#m`\n" \
                                  f"> `2020-07-29 at 11:00`\n" \
                                  f"> `11 am`"

            e_error.set_footer(text="Keep in mind that the bot timezone is UTC")

            await ctx.channel.send(embed=e_error)

        else:
            await ctx.channel.send(error)

    #
    # List
    #

    @rem.command(aliases=["ls"])
    async def list(self, ctx):
        """
        Lists reminders of a user
        """
        user_obj = ctx.author

        rems_list = await Reminder.filter(user_bind=user_obj.id).order_by("time_due_col")

        source = UserListSource(rems_list, user_obj, self.embed_colour)

        menu = menus.MenuPages(source, clear_reactions_after=True)
        await menu.start(ctx)

    #
    #
    #

    @rem.command(aliases=["lsu"])
    @commands.is_owner()
    async def list_user(self, ctx, user_id):
        """
        Lists all reminders of a user
        """
        user_obj = self.bot.get_user(user_id)

        rems_list = await Reminder.filter(user_bind=user_obj.id).order_by("time_due_col")

        source = UserListSource(rems_list, user_obj, self.embed_colour)

        menu = menus.MenuPages(source, clear_reactions_after=True)
        await menu.start(ctx)

    #
    #
    #

    @rem.command(aliases=["lsa"])
    @commands.is_owner()
    async def list_all(self, ctx):
        """Lists all reminders"""

        rems_list = await Reminder.all().order_by("time_due_col")

        source = AllListSource(rems_list, self.bot, self.embed_colour)

        menu = menus.MenuPages(source, clear_reactions_after=True)
        await menu.start(ctx)

    #
    #
    #

    @rem.command()
    async def prune(self, ctx, id_num):
        """Prunes the reminder given a specific ID"""

        user_id = ctx.author.id

        rem_prune = await Reminder.filter(rem_id=id_num).first()

        if rem_prune.user_bind != user_id and not commands.is_owner():
            raise commands.BadArgument("That is not a valid reminder to prune")

        e = discord.Embed(title="Deleted:",
                          description=str(rem_prune),
                          colour=self.embed_colour)

        user = self.bot.get_user(rem_prune.user_bind)

        e.set_footer(text=f"Reminder for {user.name}#{user.discriminator}",
                     icon_url=user.avatar_url)

        for t in asyncio.Task.all_tasks():
            if t.get_name() == f"REMIND{rem_prune.rem_id}":
                t.cancel()

        await Reminder.delete(rem_prune)
        self.rem_total -= 1

        await ctx.channel.send(embed=e)

    #
    #
    #

    @rem.command(aliases=["pu"])
    async def prune_user(self, ctx, id_num):
        """Prunes the users reminders"""
        num_rem = 0

        async for rem in Reminder.all().filter(user_bind=id_num):
            await rem.delete()
            num_rem += 1
            self.rem_total -= 1

        await ctx.send(embed=discord.Embed(title="Deleted:",
                                           description=f"{num_rem}",
                                           colour=self.embed_colour))


def setup(bot):
    bot.add_cog(ReminderCog2(bot))
    print("ReminderCog has been loaded")
