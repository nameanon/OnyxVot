import asyncio
from functools import partial

import discord
from discord.ext import commands
import itertools
import re
from discord import Client, Object, DMChannel


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

        self.last_m_logged_author = None
        self.web_to_use = None
        self._dm_log_ch = None

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):

        if type(channel) is discord.channel.DMChannel:

            async def trig_untrig(ch):
                await ch.trigger_typing()
                await asyncio.sleep(1000)
                await ch.trigger_typing()

            self.bot.loop.create_task(trig_untrig(self._dm_log_ch))

        else:
            return

    @commands.Cog.listener()
    async def on_message(self, message):

        # In DMs start case
        if type(message.channel) is discord.channel.DMChannel and not message.author.bot:

            if message.author != self.last_m_logged_author or self.web_to_use is None:
                self.web_to_use = next(self.bot_dms_web)

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

            self.last_m_logged_author = message.author
            await self.web_to_use.send(**content_dict)
            return
        # Is DMs end case

        # Is a reply to a dm

        if message.channel.id == 821032089088163900 and not message.author.bot and message.reference:

            replied_message = await message.channel.fetch_message(message.reference.message_id)

            info = re.findall(pattern=r"(\d{18})", string=replied_message.author.name)
            info = {"DMch": int(info[0]), "ID": int(info[1])}

            async def start_dm(client: Client, id: int) -> discord.DMChannel:
                user_dm = client._connection._get_private_channel_by_user(id)
                if user_dm is None:
                    user_dm = client._connection.add_dm_channel(await client.http.start_private_message(id))
                return user_dm

            DMChannel = await start_dm(self.bot, info["ID"])

            e = discord.Embed(
                colour=message.author.colour,
                description=f"{message.content}"
            )

            e.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar_url}")

            content_dict = {}
            if message.attachments:
                for a in message.attachments:
                    try:
                        content_dict["content"] = content_dict["content"] + f"\n{a.url}"
                    except KeyError:
                        content_dict["content"] = f"\n{a.url}"

            content_dict["embed"] = e

            await DMChannel.send(**content_dict)
            return

        # Is a reply to a dm end

        if message.author.bot:  # or "https://vm.tiktok.com" in message.content:
            return

        # In Fam start case

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

        # In Fam End case


async def web_init(id, cog):
    cog.ori_w = itertools.cycle(await cog.bot.get_channel(cog.ori).webhooks())
    cog.fam_w = itertools.cycle(await cog.bot.get_channel(cog.fam).webhooks())

    cog.bot_dms_web = itertools.cycle(await
                                      cog.bot.get_guild(665743810315419670)
                                      .get_channel(821032089088163900).webhooks())

    cog._dm_log_ch = next(cog.bot_dms_web).channel


def setup(bot):
    bot.add_cog(LinkCog(bot))
    print("LinkCog has been loaded")
