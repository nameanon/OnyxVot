import datetime
import itertools
import json
import random
import sys

from discord.ext import commands, tasks
import aiohttp
import discord
import re
from bs4 import BeautifulSoup


class Picture_Lib(commands.Cog, name="Picture_Lib"):

    def __init__(self, bot):
        self.bot = bot
        self.embed_colour = 1741991

        with open('TOKEN.json') as json_file:
            data = json.load(json_file)

            self.api_key = f"{data['cute_apis']['f_api_key']}"
            api_secret = f"{data['cute_apis']['f_api_secret']}"
            self.chew_token = f"{data['cute_apis']['chew']}"

        tags = ["red panda", "cute wolf", "cute fox", "wolf", "fox", "cute red panda"]
        self.flick_tags = itertools.cycle(sorted(tags, key=lambda k: random.random()))
        tags = ["fox", "wolf", "red-panda"]
        self.chew_tags = itertools.cycle(sorted(tags, key=lambda k: random.random()))

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

                e = await self.get_flick_photo_embed(tag)

                await channel.send(embed=e)


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
    async def flick(self, ctx, *, tags=None):
        """
        Searches on flickr for a picture. The picture returned is random.
        """
        if tags is None:
            tags = random.choice(["red panda", "cute wolf", "cute fox", "wolf", "fox", "cute red panda"])

        e = await self.get_flick_photo_embed(tags)

        await ctx.send(embed=e)

    #
    #
    #

    async def get_flick_photo_embed(self, tags) -> discord.Embed:
        async with aiohttp.ClientSession() as session:
            base_url = "https://www.flickr.com/services/rest/?method=flickr.photos.search"
            params = {"api_key": self.api_key,
                      "text": tags,
                      "tag_mode": "all",
                      "per_page": "250",
                      "sort": "relevance",
                      "safe_search": "1"}

            async with session.get(base_url,
                                   params=params) as resp:
                resp = await resp.read()
                soup = BeautifulSoup(resp, "lxml")
                photo_l = soup.find_all("photo")
                photo_id = random.choice(photo_l).get("id")

                base_url = "https://www.flickr.com/services/rest/?method=flickr.photos.getInfo"

                async with session.get(base_url,
                                       params={"api_key": self.api_key,
                                               "photo_id": photo_id}) as resp:
                    resp = await resp.read()
                    photo_soup = BeautifulSoup(resp, "lxml")
                    p_id = photo_soup.find("photo").get("id")
                    p_secret = photo_soup.find("photo").get("secret")
                    p_server = photo_soup.find("photo").get("server")
                    p_source_url = "https://live.staticflickr.com/" + p_server + "/" + p_id + "_" + p_secret + "_b.jpg"
                    p_title = photo_soup.find("title").getText()
                    p_url = photo_soup.find("url").getText()

                    owner_name = photo_soup.find("owner").get("username")

                    desc = photo_soup.find("description").getText()

                    e = discord.Embed(title=f"{p_title}.png",
                                      url=f"{p_url}",
                                      colour=self.embed_colour)

                    e.set_image(url=p_source_url)
                    e.set_footer(text=f"Owner of image: {owner_name}",
                                 icon_url="https://farm66.staticflickr.com/65535/buddyicons/14713082@N21_r.jpg?1585603124")

                    if "<" in desc:
                        desc_split = re.split(f'<[ab/]*>|<a[\w\s=":/.]*>', desc)
                        desc = ""
                        for d in desc_split:
                            desc.join(d)

                    if desc:
                        if len(desc) < 250:
                            e.description = f">>> {desc}"
                        else:
                            e.description = f">>> {desc[0:300]}..."

                    return e

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
                        if inp not in ['q', 'dateBegin', 'dateEnd', 'artistOrCulture', 'departmentId', "medium",
                                       "geoLocation"]:
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
