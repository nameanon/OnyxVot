import datetime
import re
from discord.ext import commands


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

    if test_chars:
        raise commands.BadArgument("Invalid character")

    if " " in chars or " " in dig:
        # print(chars, dig)
        raise commands.BadArgument("Please input the Rem correctly")

    if len(chars) != len(dig) or not chars or not dig:
        # print(chars, dig)
        raise commands.BadArgument("Please input the date correctly -> Example:`15h2m` = 15 hours and 2 minutes")

    dic = dict(zip(chars, dig))  # Creates a dic unit : amount

    for val, value in dic.items():
        if val == "s":
            res += datetime.timedelta(seconds=int(value))
        if val == "m":
            res += datetime.timedelta(minutes=int(dic[val]))
        if val == "h":
            res += datetime.timedelta(hours=int(dic[val]))
        if val == "d":
            res += datetime.timedelta(days=int(dic[val]))

    return res  # Returns added Timedelta
