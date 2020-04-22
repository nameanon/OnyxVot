import discord
from discord.ext import commands
import sys

class InfoCog(commands.Cog, name="info"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()  # Ping command
    async def info(self, ctx):
        ping = int(round(self.bot.latency, 3) * 1000)
        await ctx.send({
            "embed": {
                "title": "Information",
                "description": "```\n{sys.platform}```",
                "url": "https://discordapp.com",
                "color": 10806237,
                "footer": {
                    "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png",
                    "text": "Bot-Owner: OrionVi#0327"
                },
                "author": {
                    "name": "author name",
                    "url": "https://discordapp.com",
                    "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
                },
                "fields": [
                    {
                        "name": "Ping",
                        "value": ping
                    }
                ]
            }
        })

# TODO: Refine the info command into a workable instance

    @commands.command()  # Deletes msgs if has perms
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=10):
        await ctx.channel.purge(limit=amount)

    @commands.Cog.listener()  # Cogs listener are events in cogs
    async def on_command_error(self, ctx, error):
        await ctx.channel.send(error)


def setup(bot):
    bot.add_cog(InfoCog(bot))
    print("InfoCog has been loaded")
