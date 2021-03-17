import discord
from discord.ext import commands
import itertools


class LinkCog(commands.Cog, name="server link"):

    def __init__(self, bot):
        self.bot = bot

        self.fam = 664617672608186381
        self.ori = 742182450301632542

        self.fam_w = None
        self.ori_w = None

        self.bot.loop.create_task(web_init(self.fam, self))

        self.last_web_used_fam = None
        self.last_web_used_ori = None
        self.bot_dms_web = None

    @commands.Cog.listener()
    async def on_message(self, message):

        if type(message.channel) is discord.channel.DMChannel:
            print(message)
            web_to_use = next(self.bot_dms_web)

            content_dict = {
                "username": message.author.display_name + f" (DMCh:{message.channel.id}) (ID: {message.author.id})",
                "avatar_url": message.author.avatar_url}

            if message.content:
                content_dict["content"] = message.content

            if message.attachments:
                for a in message.attachments:
                    try:
                        content_dict["content"] = content_dict["content"] + f"\n{a.url}"
                    except KeyError:
                        content_dict["content"] = f"\n{a.url}"

            await web_to_use.send(**content_dict)
            return

        if message.author.bot:  # or "https://vm.tiktok.com" in message.content:
            return

        content_dict = {
            "username": message.author.display_name,
            "avatar_url": message.author.avatar_url}

        if message.content:
            content_dict["content"] = message.content

        if message.attachments:
            for a in message.attachments:
                try:
                    content_dict["content"] = content_dict["content"] + f"\n{a.url}"
                except KeyError:
                    content_dict["content"] = f"\n{a.url}"

        last_m = await message.channel.history(limit=1).flatten()

        if message.channel.id == self.ori:
            if last_m[0].author == message.author and self.last_web_used_fam is not None:
                web_to_use = self.last_web_used_fam

            else:
                web_to_use = next(self.fam_w)
                self.last_web_used_fam = web_to_use

            await web_to_use.send(**content_dict)

        elif message.channel.id == self.fam:
            if last_m[0].author == message.author and self.last_web_used_ori is not None:
                web_to_use = self.last_web_used_ori

            else:
                web_to_use = next(self.ori_w)
                self.last_web_used_ori = web_to_use

            await web_to_use.send(**content_dict)


async def web_init(id, cog):
    cog.ori_w = itertools.cycle(await cog.bot.get_channel(cog.ori).webhooks())
    cog.fam_w = itertools.cycle(await cog.bot.get_channel(cog.fam).webhooks())

    cog.bot_dms_web = itertools.cycle(await
                                      cog.bot.get_guild(665743810315419670)
                                      .get_channel(821032089088163900).webhooks())


def setup(bot):
    bot.add_cog(LinkCog(bot))
    print("LinkCog has been loaded")
