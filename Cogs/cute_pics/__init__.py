import datetime
import itertools
import json
import random
import sys

import flickrapi
from discord.ext import commands, tasks
import requests


class CutePics(commands.Cog, name="CutePics"):

    def __init__(self, bot):
        self.bot = bot

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

                photo_query = self.flickr.photos.search(text=tag,
                                                        tag_mode="all",
                                                        per_page="250",
                                                        sort="relevance",
                                                        safe_search="1")

                photo_list = photo_query["photos"]["photo"]
                photo_url = \
                    self.flickr.photos.getInfo(photo_id=random.choice(photo_list)["id"])["photo"]["urls"]["url"][0][
                        "_content"]

                if photo_url[-1] == "/":
                    photo_url = photo_url[:-1]

                await channel.send(photo_url)

            else:
                url = "https://api.chewey-bot.top/" + next(self.chew_tags) + self.chew_token

                with requests.get(url) as response:
                    await channel.send(response.json()["data"])

    #
    #
    #
    #
    #

    @commands.command()
    async def flick(self, ctx, *,
                    tags=random.choice(["red panda", "cute wolf", "cute fox", "wolf", "fox", "cute red panda"])):
        """
        Searches on flickr for a picture. The picture returned is random.
        """

        photo_query = self.flickr.photos.search(text=tags,
                                                tag_mode="all",
                                                per_page="250",
                                                sort="relevance",
                                                safe_search="1")

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
            with requests.get(url) as response:
                await ctx.send(response.json()["data"])

        except Exception as e:
            raise e


def setup(bot):
    bot.add_cog(CutePics(bot))
    print("CutePics has been loaded")
