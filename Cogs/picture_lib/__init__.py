import datetime
import itertools
import json
import random
import sys

import asyncio
from functools import partial

import flickrapi
from discord.ext import commands, tasks
import aiohttp
import discord
import re


class Picture_Lib(commands.Cog, name="Picture_Lib"):

    def __init__(self, bot):
        self.bot = bot
        self.embed_colour = 1741991

        with open('TOKEN.json') as json_file:
            data = json.load(json_file)

            api_key = f"{data['cute_apis']['f_api_key']}"
            api_secret = f"{data['cute_apis']['f_api_secret']}"
            self.chew_token = f"{data['cute_apis']['chew']}"

        tags = ["red panda", "cute wolf", "cute fox", "wolf", "fox", "cute red panda"]
        self.flick_tags = itertools.cycle(sorted(tags, key=lambda k: random.random()))
        tags = ["fox", "wolf", "red-panda"]
        self.chew_tags = itertools.cycle(sorted(tags, key=lambda k: random.random()))

        self.flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
        self.cute_upload.start(665743810315419670, 743113849372409858)

    #
    #
    #
    #
    #

    @tasks.loop(hours=2)
    async def cute_upload(self, guild, channel):

        if sys.platform == "win32":
            return

        channel = self.bot.get_guild(guild).get_channel(channel)
        message = await channel.history(limit=30).flatten()

        messages_per_day = [m for m in message if m.created_at.date() == datetime.datetime.utcnow().date()]
        messages_per_hour = [
            m for m in message if (datetime.datetime.utcnow() - m.created_at < datetime.timedelta(minutes=30))
        ]

        if len(messages_per_hour):
            return

        if len(messages_per_day) < 24:
            if len(messages_per_day) % 2 == 0:
                tag = next(self.flick_tags)

                to_run = partial(self.flickr.photos.search,
                                 text=tag,
                                 tag_mode="all",
                                 per_page="250",
                                 sort="relevance",
                                 safe_search="1")

                photo_query = await asyncio.get_event_loop().run_in_executor(None, to_run)

                photo_list = photo_query["photos"]["photo"]

                to_run = partial(self.flickr.photos.getInfo,
                                 photo_id=random.choice(photo_list)["id"])

                photo_url = await asyncio.get_event_loop().run_in_executor(None, to_run)

                photo_url = photo_url["photo"]["urls"]["url"][0]["_content"]

                if photo_url[-1] == "/":
                    photo_url = photo_url[:-1]

                await channel.send(photo_url)

            else:
                url = "https://api.chewey-bot.top/" + next(self.chew_tags) + self.chew_token

                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        response = await response.json()
                        await channel.send(response["data"])

    #
    #
    # w
    #
    #

    @commands.command()
    async def flick(self, ctx, *,
                    tags=random.choice(["red panda", "cute wolf", "cute fox", "wolf", "fox", "cute red panda"])):
        """
        Searches on flickr for a picture. The picture returned is random.
        """

        to_run = partial(self.flickr.photos.search,
                         text=tags,
                         tag_mode="all",
                         per_page="250",
                         sort="relevance",
                         safe_search="1")

        photo_query = await asyncio.get_event_loop().run_in_executor(None, to_run)

        photo_list = photo_query["photos"]["photo"]
        photo_url = self.flickr.photos.getInfo(photo_id=random.choice(photo_list)["id"])["photo"]["urls"]["url"][0][
            "_content"]

        if photo_url[-1] == "/":
            photo_url = photo_url[:-1]

        await ctx.send(photo_url)

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
                    await ctx.send(response["data"])

        except Exception as e:
            raise e

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

                query = re.split(r"=|\s", query)

                params = []
                params_val = []

                for index, inp in enumerate(query, 1):
                    if index % 2 != 0 and inp:
                        if inp not in ['q', 'dateBegin', 'dateEnd', 'artistOrCulture', 'departmentId', "medium", "geoLocation"]:
                            raise commands.UserInputError("Wrong params")
                        else:
                            if inp[0].isdigit():
                                params.append(int(inp))
                            else:
                                params.append(inp)
                    else:
                        params_val.append(inp)

                query = {params[i]: params_val[i] for i in range(len(params))}

            else:
                query = {"q": query}

        else:
            query = {"q": "English", "medium": "Paintings"}

        base_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true"

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=query) as response:
                response = await response.json()

                if response["total"] == 0:
                    raise commands.UserInputError("The search provided no results")

                ob_id = list(response["objectIDs"])
                ob_id = random.choice(ob_id)
                url_ob = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{ob_id}"
                async with session.get(url_ob) as response:
                    obj = await response.json()

        e = discord.Embed(title=f'{obj["title"]}',
                          description=f"> Department: {obj['department']}\n",
                          colour=self.embed_colour)

        if obj["artistDisplayName"]:
            e.description = e.description + f"> Artist: [{obj['artistDisplayName']}]({obj['artistWikidata_URL']})"

        # if obj[""]

        e.set_image(url=obj["primaryImage"])
        e.set_footer(text=obj["objectDate"])

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Picture_Lib(bot))
    print("Picture_Lib has been loaded")
