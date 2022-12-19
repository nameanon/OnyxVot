import random

import aiohttp
import discord
from discord.ext import commands


async def get_met_embed(cog, query) -> discord.Embed:
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
                      colour=cog.embed_colour)

    if obj["artistDisplayName"]:
        e.description = f"{e.description}> Artist: [{obj['artistDisplayName']}]({obj['artistWikidata_URL']})"

    # if obj[""]

    e.set_image(url=obj["primaryImage"])
    e.set_footer(text=f'Provided by The NY Metropolitan Museum of Art | Date of piece: {obj["objectDate"]}',
                 icon_url="https://media.discordapp.net/attachments/714585934603091968/755467100197486632/"
                          "Metropolitan_Museum_of_Art_logo.png")

    return e