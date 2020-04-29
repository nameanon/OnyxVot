# Git add
# Git status
# Git commit -m ""
# Same for modifications
# Git checkout <hash> reverts back to the hash point


import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="-", case_insensitive=False)
extensionsToRun = ["Cogs.info", "Cogs.reminder"]


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    ac = discord.Game("with -s")
    await bot.change_presence(status=discord.Status.online, activity=ac)


@bot.check
def check_commands(ctx):
    whitelist = [242094224672161794, 357048939503026177, 325358072770068491]
    return ctx.message.author.id in whitelist  # Blue or Ori or Alt


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


if __name__ == "__main__":
    for extension in extensionsToRun:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}")
            print(e)

    # TODO: Look into allowed_mentions
    # TODO: Maybe add an eval function

f = open("TOKEN.txt", "r")
token = f.readline()
f.close()

bot.run(token)
