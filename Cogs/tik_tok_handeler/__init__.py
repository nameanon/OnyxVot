import discord
from discord.ext import commands
import re
from Cogs.tik_tok_handeler import vid_finder_downloader as v
import os


class TikTokCog(commands.Cog, name="TikTokCog"):

    def __init__(self, bot):
        self.bot = bot
        self.vid_path = os.path.join(os.path.dirname(__file__), "video_to_send.mp4")

    @commands.Cog.listener()
    async def on_message(self, message):
        if "https://vm.tiktok.com/" in message.content and not message.author.bot:
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                              message.content)
            url = [link for link in urls if "https://vm.tiktok.com/" in link][0]

            v.get_vid(url, self.vid_path)

            author = message.author

            webhook = await message.channel.create_webhook(name="TempWeb")

            await webhook.send(username=author.display_name,
                               avatar_url=author.avatar_url,
                               file=discord.File(self.vid_path),
                               content=message.content)

            await message.delete()
            await webhook.delete()


def setup(bot):
    bot.add_cog(TikTokCog(bot))
    print("TikTokCog has been loaded")
