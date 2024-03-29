import random
import traceback

import discord
import pytz
from discord.ext import commands
import sys
import datetime
import psutil
import os
from typing import Optional
import tortoise
import asyncio


def timeStringHandler(count):
    total_s = count.seconds
    hou, rem = divmod(total_s, 3600)
    minutes, sec = divmod(rem, 60)

    return [hou, minutes, sec]


async def is_owner(ctx):
    return ctx.author.id == 242094224672161794


class InfoCog(commands.Cog, name="Info"):

    def __init__(self, bot):
        self.bot = bot
        ct = datetime.datetime.utcnow()
        ct = ct - datetime.timedelta(microseconds=ct.microsecond)
        self.startup_time = ct
        self.embed_colour = 1741991

    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

    @commands.command(aliases=["s"])  # Ping command
    async def status(self, ctx):
        """
        Displays Running Information
        """

        owner = self.bot.get_user(242094224672161794)

        ct = datetime.datetime.utcnow()
        ct = ct - datetime.timedelta(microseconds=ct.microsecond)
        uptime = ct - self.startup_time
        prefix = await self.bot.get_prefix(ctx.message)

        ping = round((round(self.bot.latency, 3) * 1000))

        desc = f"```python\nPlatform - {sys.platform}\n" \
                   f"Python - {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}\n" \
                   f"Discord - {discord.__version__}\n" \
                   f"TortoiseOrm - {tortoise.__version__}```"

        e = discord.Embed(
            title="Current Status:", description=desc, colour=self.embed_colour
        )

        e.add_field(name="Ping",
                    value=f">>> {ping} ms",
                    inline=True)

        e.add_field(name="Uptime:",
                    value=f">>> {uptime}",
                    inline=True)

        used_m = round(psutil.virtual_memory().used / 1024 / 1024)
        total_m = round(psutil.virtual_memory().total / 1024 / 1024)
        percent_m = round((used_m / total_m) * 100)

        used_p = round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024)
        percent_pm = round((used_p / total_m) * 100)

        e.add_field(name="MemoryUsage",
                    value=f">>> ({used_m - used_p} + {used_p})/{total_m} MB \nTotal Use: {percent_m}%\nBot Use: {percent_pm}%",
                    inline=False)

        e.add_field(name="Privacy Policy:",
                    value=f"Do `{prefix}privacy_policy`")

        e.add_field(name="Special Thanks To:",
                    value=">>> ■ Bluey",
                    inline=False)

        avatar_owner = f"{owner.avatar_url}".split("?size=")
        avatar_owner = avatar_owner[0]

        e.set_footer(text=f"Made by {owner.name}#{owner.discriminator} | OV @ 4.0.3",
                     icon_url=f"{avatar_owner}")

        e.set_thumbnail(url=f"{ctx.me.avatar_url}")

        await ctx.send(embed=e)

    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

    @commands.Cog.listener()  # Cogs listener are events in cogs
    async def on_command_error(self, ctx, error):

        try:
            raise error
        except:
            tb = traceback.format_exc()
            sys.stderr.write(tb)

            if hasattr(ctx.command, 'on_error'):  # Returns nothing if local error handler
                return

            perms = [perm for perm, value in ctx.me.permissions_in(ctx.channel) if value]  # Gets perms in channel

            if "embed_links" in perms:

                e_error = discord.Embed(title="Command Error")
                e_error.colour = 15158332
                e_error.description = f"{error}"
                await ctx.channel.send(embed=e_error)

            else:
                await ctx.channel.send(error)

    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

    @commands.command()
    async def user(self, ctx, user_id: Optional[str]):
        """
        Shows information about you or a specific user
        """

        ct = self.bot.get_cog("ReminderCog").ct

        if user_id is None:
            user = ctx.author
        elif user_id.isdigit():
            user = ctx.guild.get_member(int(user_id))
        else:
            user = ctx.guild.get_member_named(user_id)
            if user is None:
                raise Exception("Check the name given is correct or if the user belongs to the guild")

        e = discord.Embed(title=f"User: {user.name}#{user.discriminator}",
                          colour=user.colour)
        e.set_thumbnail(url=f"{user.avatar_url}")

        creation_date = user.created_at - datetime.timedelta(microseconds=user.created_at.microsecond)
        creation_date = pytz.utc.localize(creation_date)
        cd_differential = ct - creation_date
        e.add_field(name="Nickname:", value=f"{user.display_name}", inline=False)

        try:
            join_date = user.joined_at - datetime.timedelta(microseconds=user.joined_at.microsecond)
            join_date = pytz.utc.localize(join_date)
            jd_differential = ct - join_date

            e.add_field(name="Account Join Info:", value=f"{jd_differential}\n`{join_date}`", inline=False)
        except AttributeError:
            pass

        e.add_field(name="Account Creation Info:", value=f"{cd_differential}\n`{creation_date}`", inline=False)

        try:
            user_activity = user.activity
            e.add_field(name="Status:", value=f"{user_activity.state}")

        except AttributeError:
            pass

        try:
            e.add_field(name="Top role:", value=f"{user.top_role}")
        except AttributeError:
            pass

        try:
            if user.is_on_mobile():
                e.set_footer(text=f"On mobile | User ID: {user.id}")
            else:
                e.set_footer(text=f"User ID:{user.id}")

        except AttributeError:
            pass

        await ctx.send(embed=e)

    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):

        pag = discord.ext.commands.Paginator()

        chars = sys.exc_info()
        n = pag.max_size

        ngrams = []
        for i in range(len(chars) - n + 1):
            ngram = "".join(chars[i:i + n])
            ngrams.append(ngram)

        for n in ngrams:
            pag.add_line(n)

        await self.bot.get_channel(713388300588810260).send(f"```{event}```")

        for page in pag.pages:
            await asyncio.sleep(1)
            await self.bot.get_channel(713388300588810260).send(page)

        pag.clear()

    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

    @commands.command(aliases=["rc", "choose"])
    async def rand_choice(self, ctx, *, choice_input):
        """
        Returns a random choice given a list separated by comas
        """
        u_input = choice_input.split(",")
        e = discord.Embed(title="Result:",
                          description=f"{random.choice(u_input)}",
                          colour=self.embed_colour)

        await ctx.send(embed=e)

    @commands.command()
    async def privacy_policy(self, ctx):
        e = discord.Embed(title="Privacy policy",
                          description="If you choose to use the Service, then you agree to the collection and use of "
                                      "information in relation to this policy. The Personal Information that is "
                                      "collected is used for providing and improving the Service. Your information is "
                                      "not shared except as described in this Privacy Policy.",
                          colour=self.embed_colour)

        e.add_field(name="1. Reminders Data",
                    value=f">>> **This includes:**\n"
                          f"`User ID` - The ID of the User to remind\n"
                          f"`Description` - The msg you want to be reminded\n"
                          f"`Date` - The date and time at which the reminder is triggered\n\n"
                          f"This gets deleted with the reminder expires,\n"
                          f" which is 5 minutes after being reminded if no repeat is triggered\n"
                          f"or through request user through the delete reminder command: `-r prune [Rem_ID]`",
                    inline=False)

        e.add_field(name="2. Channel Hook Data",
                    value=f">>> **This include:** "
                          f"\n`send_task_id` - Identifier"
                          f"\n`guild_id` - Server ID"
                          f"\n`channel_id` - Channel ID"
                          f"\n`func_to_use` - Appropriate function to use"
                          f"\n`params_of_func` - If needed the query to use"
                          f"\n`time_to_send` - The time it needs to be sent in\n\n"
                          f"This can be deleted through the command `-pic remove_channel`",
                    inline=False)
        e.add_field(name="3. DMs",
                    value=">>> DMs with the bot are forwarded to a channel in the bot support server",
                    inline=False)

        await ctx.author.send(embed=e)

    @commands.command()
    async def server(self, ctx):
        """
        Returns information about the server where it's ran
        """

        guild = ctx.guild

        guild_info = {
            p: getattr(guild, p) for p in guild.__slots__ if getattr(guild, p)
        }

        guild_info["icon"] = guild.icon_url
        del guild_info["owner_id"]
        guild_info["owner"] = guild.owner

        e = discord.Embed(title=f"Server: {guild_info['name']}", colour=self.embed_colour)
        e.set_thumbnail(url=guild_info["icon"])
        del guild_info["_state"]
        guild_info["icon"] = f"[{guild_info['name']}]({guild_info['icon']})"
        guild_info["default_notifications"] = str(guild_info["default_notifications"]).split(".")[1]

        for (k, v) in guild_info.items():
            if k in ["emojis", "_members", "_channels", "_roles"]:
                v = len(v)

            if k[0] == "_":
                k = k[1:]

            if any(map(lambda x: x in k, ["afk", "owner", "id"])):
                pass

            elif "disabled" not in str(v):
                e.add_field(name=k, value=f"> {str(v)}", inline=True)

        e.set_footer(icon_url=f"{guild_info['owner'].avatar_url}", text=f"Owner: {guild_info['owner'].display_name}#"
                                                                        f"{guild_info['owner'].discriminator} | "
                                                                        f"Guild ID: {ctx.guild.id}")

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(InfoCog(bot))
    print("InfoCog has been loaded")
