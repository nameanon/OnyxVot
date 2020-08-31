# Git add
# Git status
# Git commit -m ""
# Same for modifications
# Git checkout <hash> reverts back to the hash point

import json
import sys

import logging
import discord
from discord.ext import commands
from discord.http import Route

Route.BASE = "https://discordapp.com/api/v6"  # Bluey magic code

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="-", case_insensitive=False)
extensionsToRun = ["Cogs.Info",
                   "Cogs.tik_tok_handeler",
                   "Cogs.reminderRewrite",
                   "Cogs.Voice",
                   "Cogs.server_link",
                   "Cogs.cute_pics",
                   "Cogs.help_command"]


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    ac = discord.Game("with -s")
    await bot.change_presence(status=discord.Status.online, activity=ac)

    if __name__ == "__main__":
        for extension in extensionsToRun:
            try:
                bot.load_extension(extension)
            except Exception as e:
                print(f"Failed to load extension {extension}")
                print(e)

@bot.event
async def on_error():
    e = sys.exc_info()
    emb = discord.Embed(title=f"Type: {e[0]}",
                        description=f"Value:{e[1]}")

    emb.add_field(name="Traceback:",
                  value=f"{e[2]}")

    await bot.get_channel(713388300588810260).send(embed=emb)


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
    inv_url = "https://discordapp.com/api/oauth2/authorize?client_id=700735684524244993&permissions=0&scope=bot"
    await ctx.channel.send(f"{inv_url}")


with open('TOKEN.json') as json_file:
    data = json.load(json_file)
    if sys.platform == "win32":
        token = data["d_bot_token"]["Token_veta"]
    else:
        token = data["d_bot_token"]["Token_main"]

bot.run(token)
