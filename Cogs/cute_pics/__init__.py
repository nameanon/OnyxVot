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

        self.flick_tags = itertools.cycle(
            random.shuffle(["red panda", "cute wolf", "cute fox", "wolf", "fox", "cute red panda"]))

        self.chew_tags = itertools.cycle(
            random.shuffle(["fox", "wolf", "red-panda"]))

        self.flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
        self.cute_upload.start()

    #
    #
    #
    #
    #

    @tasks.loop(hours=2)
    async def cute_upload(self):

        if sys.platform == "win32":
            return

        channel = self.bot.get_channel(743113849372409858)
        message = await channel.history(limit=30).flatten()

        messages_per_day = [m for m in message if m.created_at.date() == datetime.datetime.utcnow().date()]

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

        await ctx.send(photo_url)

    #
    #
    #
    #
    #

    @commands.command()
    async def chew(self, ctx):
        url = "https://api.chewey-bot.top/" + random.choice(["fox", "dog", "wolf", "red-panda"]) + self.chew_token

        with requests.get(url) as response:
            await ctx.send(response.json()["data"])


def setup(bot):
    bot.add_cog(CutePics(bot))
    print("CutePics has been loaded")
