import datetime
import itertools
import json
import random

import aiohttp
import discord
from discord.ext import commands, tasks

from .db_models_pics import db_init, PicUpload
from .do_upload import do_upload
from .get_flick_photo_embed import get_flick_photo_embed
from .get_met_embed import get_met_embed
from .met_query_handler import parse_query_input
from ..reminderRewrite import schedule


class Picture_Lib(commands.Cog, name="Picture_Lib"):

    def __init__(self, bot):
        self.bot = bot
        self.embed_colour = 1741991
        self.ct = datetime.datetime.utcnow() - datetime.timedelta(microseconds=datetime.datetime.utcnow().microsecond)
        self.cute_embed = None
        self.met_embed = None

        with open('TOKEN.json') as json_file:
            data = json.load(json_file)

            self.api_key = f"{data['cute_apis']['f_api_key']}"
            api_secret = f"{data['cute_apis']['f_api_secret']}"
            self.chew_token = f"{data['cute_apis']['chew']}"

        tags = ["red panda", "cute wolf", "cute fox", "wolf", "fox", "cute red panda"]
        self.flick_tags = itertools.cycle(sorted(tags, key=lambda k: random.random()))
        tags = ["fox", "wolf", "red-panda"]
        self.chew_tags = itertools.cycle(sorted(tags, key=lambda k: random.random()))

        self.toggle = 0

        self.time_updater.start()
        self.prepare_cute_embed.start()
        self.send_task = self.bot.loop.create_task(self.send_init())

    #
    #
    #
    #
    #

    @tasks.loop(seconds=1)
    async def time_updater(self):

        ct = datetime.datetime.utcnow()
        self.ct = ct - datetime.timedelta(microseconds=ct.microsecond)

    #
    #

    @tasks.loop(hours=2)
    async def prepare_cute_embed(self):

        if self.toggle == 0:

            tag = next(self.flick_tags)
            self.cute_embed = await get_flick_photo_embed(self, tag)
            self.toggle += 1

        else:
            self.toggle = 0
            tag = next(self.chew_tags)

            url = "https://api.chewey-bot.top/" + tag + self.chew_token

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response = await response.json()

                    e = discord.Embed(title=f"{tag}.png",
                                      description="",
                                      url=f"{response['data']}",
                                      colour=self.embed_colour)

                    e.set_image(url=f"{response['data']}")

                    self.cute_embed = e

        self.met_embed = await get_met_embed(self, query={"q": "English", "medium": "Paintings"})

    #
    #
    #
    #
    #

    @commands.command()
    async def flick(self, ctx, *, tags=None):
        """
        Searches on flickr for a picture. The picture returned is random.
        """
        if tags is None:
            tags = random.choice(["red panda", "cute wolf", "cute fox", "wolf", "fox", "cute red panda"])

        e = await get_flick_photo_embed(self, tags)

        await ctx.send(embed=e)

    #
    #
    #
    #
    #

    @commands.command()
    async def chew(self, ctx, *, tag=None):
        """
        Returns a random cute picture with optional tags
        """
        if tag:
            url_tags = ["birb", "car", "cat", "dog", "duck", "fantasy-art", "fox",
                        "koala", "nature", "otter", "owl", "panda", "plane", "rabbit",
                        "red-panda", "snake", "space", "turtle", "wolf"]

            if tag not in url_tags:
                error_msg = "The tag is not in the available options ====>\n"
                for t in url_tags:
                    error_msg += f" - `{t}` "

                raise commands.UserInputError(error_msg)

            else:
                url_tag = tag

        else:
            url_tag = random.choice(["fox", "dog", "wolf", "red-panda"])

        url = "https://api.chewey-bot.top/" + url_tag + self.chew_token

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response = await response.json()

                    e = discord.Embed(title=f"{url_tag}.png",
                                      description="",
                                      url=f"{response['data']}",
                                      colour=self.embed_colour)

                    e.set_image(url=f"{response['data']}")

                    await ctx.send(embed=e)

        except Exception as e:
            raise e

    #
    #
    #
    #
    #

    @commands.command(
        description="""
        Returns a ran choice form query to the NY met museum
        Available search params:
        {`q`, `dateBegin and dateEnd`, `artistOrCulture`, `departmentId`, `medium`, `geoLocation`}
        """
    )
    @commands.is_owner()
    async def met(self, ctx, *, query=None):
        """
        Returns a ran choice form query to the NY met museum
        Available search params: {q, dateBegin and dateEnd, artistOrCulture, departmentId, medium, geoLocation}
        """
        if query:
            if "=" in query:
                query = parse_query_input(query)
                print(query)
            else:
                query = {"q": query}

        else:
            query = {"q": "English", "medium": "Paintings"}

        e = await get_met_embed(self, query)

        await ctx.send(embed=e)

    #
    #
    #
    #
    #

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def pic(self, ctx):
        """
        The group to manage periodic uploads to specific channels
        """
        await ctx.send_help(self.pic)

    @pic.command(aliases=["add", "set"])
    async def set_channel(self, ctx, channel_id: int, func, *, params=None):
        """
        Adds a channel for periodic upload. func=(cute|met)
        """

        channel = ctx.guild.get_channel(channel_id)
        print(channel)

        if func not in ["cute", "met"]:
            raise commands.BadArgument("The function is not supported")

        if channel is None:
            raise commands.BadArgument("The channel does not exist or is not part of this server")

        present = await PicUpload.filter(guild_id=ctx.guild.id).all().count()

        if present >= 2:
            raise commands.CommandError("Maximum number of channels reached")

        chan_hook = await PicUpload.create(guild_id=ctx.guild.id,
                                           channel_id=channel.id,
                                           func_to_use=func,
                                           params_of_func=params,
                                           time_to_send=self.ct)

        await do_upload(self, chan_hook)

        await ctx.send(embed=discord.Embed(title="Added the channel: ",
                                           description=f"{chan_hook}",
                                           colour=self.embed_colour))

    @pic.command(aliases=["remove"])
    async def remove_channel(self, ctx, channel_id: int):
        """
        Removes the channel from active upload
        """

        dest_to_prune = await PicUpload.filter(guild_id=ctx.guild.id).filter(channel_id=channel_id).first()

        if dest_to_prune is not None:
            await dest_to_prune.delete()

            await ctx.send(embed=discord.Embed(title="Removed channel:",
                                               description=f"**Channel:** <#{channel_id}>",
                                               colour=self.embed_colour))

        else:
            raise commands.BadArgument("The channel does not exist or is not part of this server")

    @pic.command(aliases=["ls", "list"])
    async def list_channels(self, ctx):
        """
        Lists active channels in guild
        """
        dest_in_guild = await PicUpload.filter(guild_id=ctx.guild.id).all()

        e = discord.Embed(title="Channels:",
                          description="",
                          colour=self.embed_colour)

        for dest in dest_in_guild:
            e.description = e.description + f"\n {dest}"

        await ctx.send(embed=e)

    #
    #
    #
    #
    #

    async def send_init(self):
        async for dest_hook in PicUpload.all():
            self.bot.loop.create_task(schedule(dest_hook.time_to_send, do_upload, self, dest_hook),
                                      name=f"SEND_TASK - {dest_hook.send_task_id}")


def setup(bot):
    bot.add_cog(Picture_Lib(bot))
    print("Picture_Lib has been loaded")
