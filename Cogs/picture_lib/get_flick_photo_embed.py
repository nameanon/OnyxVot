import random
import re

import aiohttp
import discord
from bs4 import BeautifulSoup


async def get_flick_photo_embed(cog, tags) -> discord.Embed:
    async with aiohttp.ClientSession() as session:
        base_url = "https://www.flickr.com/services/rest/?method=flickr.photos.search"
        params = {"api_key": cog.api_key,
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

            async with session.get(base_url, params={"api_key": cog.api_key,
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
                                  colour=cog.embed_colour)

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