# pip install requests
# pip install beautifulsoup4
# pip insatall selenium
# pip install TikTokApi
# pyppeteer-install

import aiohttp
from bs4 import BeautifulSoup
import re
import discord
import io

url_try = "https://vm.tiktok.com/3Namrp/"


async def src_finder(url_to_find):
    user = "Mozilla/5.0 (Linux; Android 4.2.2; nl-nl; SAMSUNG GT-I9505 Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Version/1.0 Chrome/18.0.1025.308 Mobile Safari/535.19"

    async with aiohttp.ClientSession(headers={'User-Agent': user}) as session:
        async with session.get(url_to_find) as response:
            page_content = await response.text()
            soup = BeautifulSoup(page_content, "html.parser")

    # page = requests.get(url_to_find, headers={'User-Agent': user})
    # soup = BeautifulSoup(page.content, "html.parser")

    a = soup.prettify()
    line = [line for line in a.split("\n") if "window.__INIT_PROPS__" in line][0]

    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)

    url = [link for link in urls if "type=video" in link]

    if len(url) > 1:
        raise Exception("Help")
    else:
        return url[0]


async def get_vid(url):
    url = await src_finder(url)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp = await resp.read()
            return discord.File(filename="Tik.mp4",
                                fp=io.BytesIO(resp))
