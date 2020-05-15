import asyncio
import discord
from discord.ext import commands, tasks
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
import re


async def is_owner(ctx):
    return ctx.author.id == 242094224672161794


def get_datetime_obj(st: str) -> datetime.timedelta:
    """
    Takes a string with #d#h#m#s and returns a time delta object of the string
    """

    res = datetime.timedelta()  # Initializes res

    dig = re.split(r"\D+", st)  # Splits on non digits
    dig = [e for e in dig if e != ""]  # Removes empties

    chars = re.split(r"\d+", st)  # Splits on digits
    chars = [e for e in chars if (e in "smhd" and e != "")]  # Removes empties

    test_chars = [c for c in chars if c not in "smhd"]

    if len(test_chars) != 0:
        raise Exception("Invalid character")

    if " " in chars or " " in dig:
        print(chars, dig)
        raise Exception("Don't use spaces in the input")

    if len(chars) != len(dig):
        print(chars, dig)
        raise Exception("Please input the date correctly -> Example:`15h2m` = 15 hours and 2 minutes")

    dic = dict(zip(chars, dig))  # Creates a dic unit : amount

    for val in dic:
        if val == "s":
            res += datetime.timedelta(seconds=int(dic[val]))
        if val == "m":
            res += datetime.timedelta(minutes=int(dic[val]))
        if val == "h":
            res += datetime.timedelta(hours=int(dic[val]))
        if val == "d":
            res += datetime.timedelta(days=int(dic[val]))

    return res  # Returns added Timedelta


#
#
#
# ----- DB -----
#
#

ap = os.path.abspath(__file__)
ap = ap[:len(ap) - 11]

engine = create_engine(f"sqlite:///{ap}db_files/rem.db", echo=False)

Base = declarative_base()


class Reminder(Base):
    __tablename__ = "Reminders"

    rem_id = Column(Integer(), primary_key=True)
    desc = Column(String(100))
    time_due_col = Column(DateTime)
    user_bind = Column(Integer())
    time_differential = Column(Interval)

    def __repr__(self):
        ct = datetime.datetime.now()
        ct = ct - datetime.timedelta(microseconds=ct.microsecond)
        due = self.time_due_col - ct
        return f"{self.rem_id}. {self.desc} due in {due}"

    def __str__(self):
        ct = datetime.datetime.now()
        ct = ct - datetime.timedelta(microseconds=ct.microsecond)
        due = self.time_due_col - ct
        return f"{self.desc} due in {due}"


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, expire_on_commit=False)
session = Session()


def create_embed_list(rem_list) -> discord.Embed:
    """
    :param rem_list:
    :return embed:

    creates embed from list containing and ordering reminders
    """

    e = discord.Embed(title="Reminders:",
                      colour=1741991)

    if len(rem_list) != 0:
        res_str = ""
        for r in rem_list:
            res_str += str(r.rem_id) + ". " + str(r)
            res_str += "\n"

            e.add_field(name=f"ID: {r.rem_id}",
                        value=str(r),
                        inline=False)

    else:
        e = discord.Embed(title="No Reminders Present :)", colour=1741991)

    return e


class ReminderCog(commands.Cog, name="ReminderCog"):

    def __init__(self, bot):
        self.bot = bot
        ct = datetime.datetime.now()
        self.ct = ct - datetime.timedelta(microseconds=ct.microsecond)
        self.time_updater.start()
        self.db_pruner.start()  # Starts the background task that deletes overdue reminders

    #
    #
    #
    #
    #
    #
    #
    #
    #
    # ----- Loops -----

    async def remind(self):
        """

        Sends reminder to user when ct coincides with time in a reminder,
        The dm also has a reaction that if reacted to within a timeout will remind again after the interval

        """

        rems_test = [remind for remind in session.query(Reminder).filter(Reminder.time_due_col == self.ct)]

        if len(rems_test) != 0:
            user = self.bot.get_user(rems_test[0].user_bind)
            msg = await user.send(f"**Reminder: **{rems_test[0].desc}")

            # Adds reaction to previous msg

            reaction = await msg.add_reaction("🔁")

            def check(reaction, user):
                print(reaction, user)
                print(str(reaction.emoji) == "🔁" and reaction.count != 1)
                return str(reaction.emoji) == "🔁" and reaction.count != 1

            try:
                print("Trying")
                reaction2, user = await self.bot.wait_for('reaction_add', timeout=300, check=check)


            except asyncio.TimeoutError:
                print("TimeOut Case")
                await msg.remove_reaction("🔁", msg.author)
                session.delete(rems_test[0])

            else:
                rems_test[0].time_due_col = self.ct + rems_test[0].time_differential
                await msg.add_reaction("✅")

            session.commit()
            session.close()

    @tasks.loop(seconds=1)
    async def time_updater(self):
        """
        Updates the current time variable
        """

        ct = datetime.datetime.now()
        self.ct = ct - datetime.timedelta(microseconds=ct.microsecond)

        await self.remind()

    @tasks.loop(hours=12)
    async def db_pruner(self):
        """
        Deletes all reminders on the db that have already passed
        """

        exp_reminders = [remind for remind in session.query(Reminder).filter(Reminder.time_due_col < self.ct)]

        for r in exp_reminders:
            session.delete(r)

        session.commit()
        session.close()

        #
        #
        #
        #
        #
        #
        #
        #
        #
        # ----- Commands -----

    @commands.command(aliases=["t", "ct"])
    async def current_time(self, ctx):
        """
        Sends the current time variable
        """
        await ctx.channel.send(f"{self.ct}")

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

    @commands.group(name="r", invoke_without_command=True)
    async def rem(self, ctx):
        if await is_owner(ctx):
            e = discord.Embed(title="Reminder Module:",
                              description="Commands supported: \n"
                                          "1.`list` - Lists all your reminders\n"
                                          "2.`list_user [user id]`\n"
                                          "3.`list_all` - Lists all reminders on the db\n"
                                          "4.`me [description] in [time]`\n"
                                          "5.`prune [reminder id as shown in list]` - Deletes Reminder\n"
                                          "6.`prune_user [user_id]` (Owner Only)\n"
                                          "7.`db_rollback` (Owner Only)",
                              colour=1741991)

        else:
            e = discord.Embed(title="Reminder Module:",
                              description="Commands supported:\n"
                                          "1.`list` - Lists all your reminders\n"
                                          "2.`me [description] in [time]`\n"
                                          "3.`prune [reminder id as shown in list]` - Deletes Reminder\n",
                              colour=1741991)

        await ctx.send(embed=e)

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

    @rem.command(aliases=["ls"])
    async def list(self, ctx):
        """
        Lists first 25 reminders of a user
        """

        query = session.query(Reminder)

        user_obj = ctx.author
        rems_list = [remind for remind in
                     query.filter(Reminder.user_bind == user_obj.id).order_by(Reminder.time_due_col)]

        if len(rems_list) > 25:
            e = create_embed_list(rems_list[:25])
            e.set_footer(icon_url=str(user_obj.avatar_url),
                         text=f"Reminders for {user_obj.name}  |  1-25 of {len(rems_list)}")

        else:
            e = create_embed_list(rems_list)
            e.set_footer(icon_url=str(user_obj.avatar_url),
                         text=f"Reminders for {user_obj.name}")

        await ctx.channel.send(embed=e)

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

    @rem.command(aliases=["lsu"])
    @commands.check(is_owner)
    async def list_user(self, ctx, user_id):
        """
        :param ctx:
        :param user_id:
        :return:

        Lists all the reminders of a specific user
        """

        query = session.query(Reminder)

        user_obj = self.bot.get_user(int(user_id))

        rems_list = [remind for remind in
                     query.filter(Reminder.user_bind == user_obj.id).order_by(Reminder.time_due_col)]

        if len(rems_list) > 25:
            e = create_embed_list(rems_list[:25])
            e.set_footer(icon_url=str(user_obj.avatar_url),
                         text=f"Reminders for {user_obj.name}  |  1-25 of {len(rems_list)}")

        else:
            e = create_embed_list(rems_list)
            e.set_footer(icon_url=str(user_obj.avatar_url),
                         text=f"Reminders for {user_obj.name}")

        await ctx.channel.send(embed=e)

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

    @rem.command(aliases=["lsa"])
    @commands.check(is_owner)
    async def list_all(self, ctx):
        """Lists all reminders"""

        query = session.query(Reminder)

        rems_list = [remind for remind in query.order_by(Reminder.time_due_col)]

        if len(rems_list) != 0:
            res_str = ""
            for r in rems_list:
                user_name = self.bot.get_user(int(r.user_bind)).name
                res_str += str(r.rem_id) + ". " + str(r) + f" by {user_name}"
                res_str += "\n"

            e = discord.Embed(title="Reminders:",
                              description=res_str,
                              colour=1741991)

        else:
            e = discord.Embed(title="No Reminders Present :)", colour=1741991)

        e.set_footer(text=f"Reminders for all users")

        await ctx.channel.send(embed=e)

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

    @rem.command(name="me")
    async def me(self, ctx, rem_dsc, junk_in, obj_time_due: get_datetime_obj):
        """
        :param ctx:
        :param rem_dsc:
        :param junk_in:
        :param obj_time_due:
        :return:

        Main reminder command

        """

        if junk_in != "in":
            raise commands.BadArgument("Wrong command format")

        if len(rem_dsc) > 240:
            raise commands.BadArgument("The remainders can't exceed 240 characters")

        time_due = self.ct + obj_time_due
        r = Reminder(desc=rem_dsc,
                     time_due_col=time_due,
                     user_bind=ctx.author.id,
                     time_differential=obj_time_due)
        session.add(r)

        e = discord.Embed(title="Added:",
                          description=r.__str__(),
                          colour=1741991)

        await ctx.channel.send(embed=e)

        session.commit()
        session.close()

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

    @rem.command()
    async def prune(self, ctx, id_num):
        """ Prunes the users reminders"""

        user = ctx.author.id

        rem_prune = session.query(Reminder).filter(Reminder.rem_id == id_num).first()
        if rem_prune.user_bind == user:
            e = discord.Embed(title="Deleted:",
                              description=str(rem_prune),
                              colour=1741991)

            session.delete(rem_prune)
            session.commit()
            session.close()

        else:
            raise Exception("That is not a valid reminder to prune")

        await ctx.channel.send(embed=e)

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

    @rem.command()
    @commands.check(is_owner)
    async def prune_user(self, ctx, id_num):
        """
        Prunes a specific users reminders

        :param ctx:
        :param id_num:
        :return:
        """

        user_to_rem = self.bot.get_user(id_num)

        rem_prune = [rem for rem in session.query(Reminder).filter(Reminder.user_bind == user_to_rem)]

        desc_deletion = ""

        for rem in rem_prune:
            desc_deletion += str(rem.rem_id) + ". " + str(rem)
            desc_deletion += "\n"
            session.delete(rem)

        e = discord.Embed(title="Deleted:", description=str(desc_deletion), colour=1741991)

        session.commit()
        session.close()

        await ctx.channel.send(embed=e)

    #  TODO: Modify the filter to make it prettier
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

    @rem.command()
    @commands.check(is_owner)
    async def db_rollback(self, ctx):
        """
        Rolls back the db if needed
        """
        session.rollback()
        await ctx.send("Roll back!")


def setup(bot):
    bot.add_cog(ReminderCog(bot))
    print("ReminderCog has been loaded")
