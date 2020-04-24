import discord
from discord.ext import commands
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


## TODO: Review code with what Bluey sent
## TODO: aioschedule

engine = create_engine("sqlite:///rem.db", echo=False)

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


class Reminder(Base):
    __tablename__ = "Reminders"

    rem_id = Column(Integer(), primary_key=True)
    desc = Column(String(100))
    time_min = (Integer)



class ReminderCog(commands.Cog, name="dbReminderModule"):

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(TimeCog(bot))
    print("ReminderCog has been loaded")
