
# Git add
# Git status
# Git commit -m ""
# Same for modifications
# Git checkout <hash> reverts back to the hash point



import discord
from discord.ext import  commands

bot = commands.Bot(command_prefix="!")
inital_extensions = ["Cogs.time"]



@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")



if __name__ == "__main__":
    for extension in inital_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}")



f = open("TOKEN.txt","r")
token = f.readline()
f.close()

bot.run(token)