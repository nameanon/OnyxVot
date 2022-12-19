import discord
from discord.ext import commands
import re
from Cogs.tik_tok_handeler import vid_finder_downloader as v
import os


class TikTokCog(commands.Cog, name="TikTokCog"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if "https://vm.tiktok.com/" not in message.content or message.author.bot:
            return
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                          message.content)
        url = [link for link in urls if "https://vm.tiktok.com/" in link][0]

        author = message.author

        file = await v.get_vid(url)

        if message.channel.id in [742182450301632542, 664617672608186381] and message.attachments == []:

            await message.delete()

            web_con = [742182450301632542, 664617672608186381]

            for ch_id in web_con:
                channel = self.bot.get_channel(ch_id)

                webhook = await channel.create_webhook(name="TempWeb")

                await webhook.send(username=author.display_name,
                                   avatar_url=author.avatar_url,
                                   file=file,
                                   content=message.content)

                await webhook.delete()


        else:

            webhook = await message.channel.create_webhook(name="TempWeb")

            await webhook.send(username=author.display_name,
                               avatar_url=author.avatar_url,
                               file=file,
                               content=message.content)

            await message.delete()
            await webhook.delete()


def setup(bot):
    bot.add_cog(TikTokCog(bot))
    print("TikTokCog has been loaded")
