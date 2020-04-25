# Git add
# Git status
# Git commit -m ""
# Same for modifications
# Git checkout <hash> reverts back to the hash point


import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="-",case_insensitive=False)
extensionsToRun = ["Cogs.info", "Cogs.reminder"]


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    ac = discord.Game("with -s")
    await bot.change_presence(status=discord.Status.online, activity=ac)


@bot.check
def check_commands(ctx):
    return ctx.message.author.id == 242094224672161794


@bot.command(aliases=["sh"])
async def shutdown(ctx):
    await ctx.channel.send(f"Shutting down... \n")
    await bot.close()



if __name__ == "__main__":
    for extension in extensionsToRun:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}")
            print(e)


f = open("TOKEN.txt", "r")
token = f.readline()
f.close()

bot.run(token)
