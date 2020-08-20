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


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot or "https://vm.tiktok.com" in message.content:
            return

        content_dict = {}
        content_dict["username"] = message.author.display_name
        content_dict["avatar_url"] = message.author.avatar_url

        if message.content:
            content_dict["content"] = message.content

        if message.attachments:
            for a in message.attachments:
                try:
                    content_dict["content"] = content_dict["content"] + f"\n{a.url}"
                except KeyError:
                    content_dict["content"] = f"\n{a.url}"

        if message.channel.id == self.ori:
            last_m = await message.channel.history(limit=1).flatten()
            if last_m[0].author == message.author and self.last_web_used_fam is not None:
                web_to_use = self.last_web_used_fam

            else:
                web_to_use = next(self.fam_w)
                self.last_web_used_fam = web_to_use

            await web_to_use.send(**content_dict)

        elif message.channel.id == self.fam:
            last_m = await message.channel.history(limit=1).flatten()
            if last_m[0].author == message.author and self.last_web_used_ori is not None:
                web_to_use = self.last_web_used_ori

            else:
                web_to_use = next(self.ori_w)
                self.last_web_used_ori = web_to_use

            await web_to_use.send(**content_dict)



async def web_init(id, cog):
    cog.ori_w = itertools.cycle(await cog.bot.get_channel(cog.ori).webhooks())
    cog.fam_w = itertools.cycle(await cog.bot.get_channel(cog.fam).webhooks())






def setup(bot):
    bot.add_cog(LinkCog(bot))
    print("LinkCog has been loaded")