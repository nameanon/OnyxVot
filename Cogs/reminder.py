import discord
from discord.ext import commands, tasks
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
import re
from .info import timeStringHandler

ap = os.path.abspath(__file__)
ap = ap[:len(ap) - 11]

engine = create_engine(f"sqlite:///{ap}db_files/rem.db", echo=False)

Base = declarative_base()


class Reminder(Base):
    __tablename__ = "Reminders"

    rem_id = Column(Integer(), primary_key=True)
    desc = Column(String(100))
    timeDue = Column(DateTime)
    user_bind = Column(Integer())

    def __repr__(self):
        due = self.timeDue - datetime.datetime.now()
        due = timeStringHandler(due)
        str_due = f"{due[0]}:{due[1]}:{due[2]}"
        return f"{self.rem_id}. {self.desc} due in {str_due}"

    def __str__(self):
        due = self.timeDue - datetime.datetime.now()
        due = timeStringHandler(due)
        str_due = f"{due[0]}:{due[1]}:{due[2]}"
        return f"{self.desc} due in {str_due}"


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, expire_on_commit=False)
session = Session()


def getDatetimeObj(st: str) -> datetime.timedelta:
    res = datetime.timedelta()  # Initializes res

    dig = re.split(r"\D+", st)  # Splits on non digits
    dig = [e for e in dig if e != ""]  # Removes empties

    chars = re.split(r"\d+", st)  # Splits on digits
    chars = [e for e in chars if e != ""]  # Removes empties

    if " " in chars or " " in dig:
        raise Exception("Don't use spaces in the input")

    dic = dict(zip(chars, dig))  # Creates a dic unit : amount

    for val in dic:
        if val == "m":
            res += datetime.timedelta(minutes=int(dic[val]))
        if val == "h":
            res += datetime.timedelta(hours=int(dic[val]))
        if val == "d":
            res += datetime.timedelta(days=int(dic[val]))

    return res  # Returns added Timedelta


class ReminderCog(commands.Cog, name="ReminderCog"):

    def __init__(self, bot):
        self.bot = bot
        self.currentTime = datetime.datetime.now()

    @tasks.loop(seconds=1)
    async def timeUpdater(self):
        self.currentTime = tm = datetime.datetime.now()

        # TODO: Make it so the test actually works

        test_date = tm - datetime.timedelta(microseconds=tm.microsecond)

        rems_test = [remind for remind in session.query(Reminder).filter(Reminder.timeDue == test_date)]

        if len(rems_test) != 0:
            user = self.bot.get_user(rems_test[0].user_bind)
            await user.send("Hi hi.")

    @commands.command(aliases=["t", "ct"])
    async def currentTime(self, ctx):
        await ctx.channel.send(f"{self.currentTime}")

    @commands.group(name="r", invoke_without_command=True)
    async def rem(self, ctx, *args):
        pass

    @rem.command()
    async def list(self, ctx):

        # TODO: Make it so only the reminders from the user appear

        rems_list = [remind for remind in session.query(Reminder)]

        if len(rems_list) != 0:

            res_str = ""
            for r in rems_list:
                res_str += str(r.rem_id) + ". " + str(r)
                res_str += "\n"

            e = discord.Embed(title="Reminders:",
                              description=res_str)

        else:
            e = discord.Embed(title="No Reminders Present :)")

        await ctx.channel.send(embed=e)

    @rem.command()
    async def me(self, ctx, desc, junck_in, str_time_due):

        if junck_in != "in":
            desc = junck_in

        time_due = self.currentTime + getDatetimeObj(str_time_due)
        r = Reminder(desc=desc, timeDue=time_due, user_bind=ctx.author.id)
        session.add(r)

        e = discord.Embed(title="Added:",
                          description=r.__str__())

        await ctx.channel.send(embed=e)

        session.commit()
        session.close()

    @rem.command()
    async def prune(self, ctx, ID):

        rem_prune = session.query(Reminder).filter(Reminder.rem_id == ID).first()

        e = discord.Embed(title="Deleted:", description=str(rem_prune))

        session.delete(rem_prune)
        session.commit()
        session.close()

        await ctx.channel.send(embed=e)


def setup(bot):
    bot.add_cog(ReminderCog(bot))
    print("ReminderCog has been loaded")
