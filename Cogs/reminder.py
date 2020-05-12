import asyncio
import discord
from discord.ext import commands, tasks
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
import re
from typing import Optional


async def is_owner(ctx):
    return ctx.author.id == 242094224672161794


def get_datetime_obj(st: str) -> datetime.timedelta:
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


class ReminderCog(commands.Cog, name="ReminderCog"):

    def __init__(self, bot):
        self.bot = bot
        ct = datetime.datetime.now()
        self.ct = ct - datetime.timedelta(microseconds=ct.microsecond)
        self.time_updater.start()
        self.db_pruner.start()

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
        ct = datetime.datetime.now()
        self.ct = ct - datetime.timedelta(microseconds=ct.microsecond)

        await self.remind()

    @tasks.loop(hours=12)
    async def db_pruner(self):

        exp_reminders = [remind for remind in session.query(Reminder).filter(Reminder.time_due_col < self.ct)]

        for r in exp_reminders:
            session.delete(r)

        session.commit()
        session.close()

    @commands.command(aliases=["t", "ct"])
    async def current_time(self, ctx):
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
    # ----- Commands -----

    @commands.group(name="r", invoke_without_command=True)
    async def rem(self, ctx, *args):
        e = discord.Embed(title="Reminder Module:",
                          description="Commands supported: \n"
                                      "1.`list : Lists all your reminders `\n"
                                      "2.`me : [description] in [time]`\n"
                                      "3.`prune : [reminder id as shown in list]` - Deletes Reminder\n"
                                      "4.`prune_user : [user_id]` (Owner Only)"
                                      "5. `db_rollback` (Owner Only)",
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
    async def list(self, ctx, user_id: Optional[str]):

        #  TODO: Fix ls so that other users doing the ls all or id options get a msg
        #  TODO: Move ALl to owner category instead

        at = 0
        query = session.query(Reminder)

        if user_id is None:
            at = ctx.author.id
            rems_list = [remind for remind in query.filter(Reminder.user_bind == at).order_by(Reminder.time_due_col)]

        elif (user_id is not None) and await is_owner(ctx) and (user_id != "all"):
            at = int(user_id)
            rems_list = [remind for remind in query.filter(Reminder.user_bind == at).order_by(Reminder.time_due_col)]

        if user_id == "all" and await is_owner(ctx):
            rems_list = [remind for remind in query.order_by(Reminder.time_due_col)]

        if len(rems_list) != 0:

            res_str = ""
            for r in rems_list:
                res_str += str(r.rem_id) + ". " + str(r)
                res_str += "\n"

            e = discord.Embed(title="Reminders:",
                              description=res_str,
                              colour=1741991)

        else:
            e = discord.Embed(title="No Reminders Present :)", colour=1741991)

        if at != 0:
            e.set_footer(icon_url=str(self.bot.get_user(at).avatar_url),
                         text=f"Reminders for {self.bot.get_user(at).name}")

        else:
            # TODO make it so when ls all is invoked it shows who did what reminder
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

        if junk_in != "in":
            raise commands.BadArgument("Wrong command format")

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
    #  TODO: Make list be able to deal with more than 2500 reminders

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
        session.rollback()
        await ctx.send("Roll back!")


def setup(bot):
    bot.add_cog(ReminderCog(bot))
    print("ReminderCog has been loaded")
