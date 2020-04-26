import discord
from discord.ext import commands, tasks
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
import re

ap = os.path.abspath(__file__)
ap = ap[:len(ap) - 11]

engine = create_engine(f"sqlite:///{ap}db_files/rem.db", echo=False)

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


class Reminder(Base):
    __tablename__ = "Reminders"

    rem_id = Column(Integer(), primary_key=True)
    desc = Column(String(100))
    timeDue = Column(DateTime)


Base.metadata.create_all(engine)


def getDatetimeObj(st: str) -> datetime.timedelta:
    res = datetime.timedelta()  # Initializes res

    dig = re.split(r"\D+", st)  # Splits on non digits
    dig = [e for e in dig if e != ""]  # Removes empties
    print(dig)

    chars = re.split(r"\d+", st)  # Splits on digits
    chars = [e for e in chars if e != ""]  # Removes empties
    print(chars)

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
        self.currentTime = datetime.datetime.now()

    @commands.command(aliases=["t", "ct"])
    async def currentTime(self, ctx):
        await ctx.channel.send(f"{self.currentTime}")

    @commands.group(name="rem", invoke_without_command=True)
    async def rem(self, ctx, *args):
        pass

    @rem.command()
    async def list(self, ctx):
        rems_list = [remind for remind in session.query(Reminder)]

        if len(rems_list) != 0:
            e = discord.Embed(title="Reminders:",
                              description=rems_list)
        else:
            e = discord.Embed(title="No Reminders Present :)")

        await ctx.channel.send(embed=e)


def setup(bot):
    bot.add_cog(ReminderCog(bot))
    print("ReminderCog has been loaded")
