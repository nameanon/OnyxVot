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


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
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
            web_to_use = next(self.fam_w)
            await web_to_use.send(**content_dict)

        elif message.channel.id == self.fam:
            web_to_use = next(self.ori_w)
            await web_to_use.send(**content_dict)



async def web_init(id, cog):
    cog.ori_w = itertools.cycle(await cog.bot.get_channel(cog.ori).webhooks())
    cog.fam_w = itertools.cycle(await cog.bot.get_channel(cog.fam).webhooks())






def setup(bot):
    bot.add_cog(LinkCog(bot))
    print("LinkCog has been loaded")