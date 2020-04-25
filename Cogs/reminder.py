import discord
from discord.ext import commands,tasks
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import aioschedule as schedule

## TODO: Review code with what Bluey sent
## TODO: aioschedule

# engine = create_engine("sqlite:///rem.db", echo=False)
#
# Base = declarative_base()
#
# Session = sessionmaker(bind=engine)
# session = Session()
#
#
# class Reminder(Base):
#     __tablename__ = "Reminders"
#
#     rem_id = Column(Integer(), primary_key=True)
#     desc = Column(String(100))
#     timeDue = Column(DateTime)


class ReminderCog(commands.Cog, name="ReminderCog"):

    def __init__(self, bot):
        self.bot = bot
        self.currentTime = datetime.datetime.now()

    @tasks.loop(seconds=1)
    async def timeUpdater(self):
        self.currentTime = datetime.datetime.now()


    @commands.command(aliases=["t","ct"])
    async def currentTime(self,ctx):
        await ctx.channel.send(f"{self.currentTime}")


def setup(bot):
    bot.add_cog(ReminderCog(bot))
    print("ReminderCog has been loaded")
