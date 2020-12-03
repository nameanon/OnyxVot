# Git add
# Git status
# Git commit -m ""
# Same for modifications
# Git checkout <hash> reverts back to the hash point

import json
import os
import sys

import logging

import asyncio
import discord
from discord.ext import commands
from discord.http import Route
from tortoise import Tortoise

Route.BASE = "https://discordapp.com/api/v6"  # Bluey magic code

logging.basicConfig(level=logging.INFO)
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="-", case_insensitive=False, intents=intents)
extensionsToRun = ["Cogs.Info",
                   #  "Cogs.tik_tok_handeler",
                   "Cogs.reminderRewrite",
                   "Cogs.Voice",
                   "Cogs.server_link",
                   "Cogs.picture_lib",
                   "Cogs.help_command",
                   "Cogs.mod_lib"]


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    ac = discord.Game("with -s")
    await bot.change_presence(status=discord.Status.online, activity=ac)

    db_con = bot.loop.create_task(db_init("rem.db"))
    await asyncio.wait([db_con])

    if __name__ == "__main__":
        for extension in extensionsToRun:
            try:
                bot.load_extension(extension)
            except Exception as e:
                print(f"Failed to load extension {extension}")
                print(e)


# @bot.event
# async def on_error():
#     e = sys.exc_info()
#     emb = discord.Embed(title=f"Type: {e[0]}",
#                         description=f"Value:{e[1]}")
#
#     emb.add_field(name="Traceback:",
#                   value=f"{e[2]}")
#
#     await bot.get_channel(713388300588810260).send(cute_embed=emb)


@bot.check
def check_commands(ctx):
    # whitelist = [242094224672161794, 357048939503026177, 325358072770068491]
    blacklist = []
    return ctx.message.author.id not in blacklist


async def is_owner(ctx):
    return ctx.author.id == 242094224672161794


@bot.command(aliases=["sh"])
@commands.check(is_owner)
async def shutdown(ctx):
    await ctx.channel.send(f"Shutting down... \n")
    await bot.close()


@bot.command(aliases=["i"])
@commands.check(is_owner)
async def invite(ctx):
    inv_url = f"<https://discordapp.com/api/oauth2/authorize?client_id={ctx.me.id}&permissions=0&scope=bot>"
    await ctx.channel.send(f"{inv_url}")

ap = os.path.abspath(__file__)
ap = ap[:len(ap) - 8]


async def db_init(db_name):
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await Tortoise.init(
        db_url=f'sqlite:///{ap}/Cogs/db_files/{db_name}',
        modules={'models': ['Cogs.reminderRewrite', 'Cogs.picture_lib']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()


with open('TOKEN.json') as json_file:
    data = json.load(json_file)
    if sys.platform == "win32":
        token = data["d_bot_token"]["Token_veta"]
    else:
        token = data["d_bot_token"]["Token_main"]

bot.run(token)
