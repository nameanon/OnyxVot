import datetime

import discord
from discord.ext import commands


class ModCog(commands.Cog, name="Mod_Lib"):

    def __init__(self, bot):
        self.bot = bot
        self.embed_colour = 1741991
        self.mod_channel_sc_id = (665743810315419670, 753959571369885777)
        self._des = bot.get_guild(self.mod_channel_sc_id[0]).get_channel(self.mod_channel_sc_id[1])

    #
    #
    #

    @commands.command(aliases=["pur"])  # Deletes msgs if has perms
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=9):
        """
        Deletes msgs in a channel, Default amount: 10
        """

        await ctx.channel.purge(limit=amount + 1)

        if ctx.guild.id == self.mod_channel_sc_id[0]:

            e = discord.Embed(title=f"Mod action:",
                              description=f"{ctx.author.mention} purged {amount + 1} msgs",
                              colour=self.embed_colour)

            e.add_field(name="Channel: ",
                        value=f"<#{ctx.channel.id}>")

            e.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",
                         icon_url=f"{ctx.author.avatar_url}")

            await self._des.send(embed=e)

        else:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == self.mod_channel_sc_id[0]:
            e = discord.Embed(title=f"Member Event:",
                              description=f"{member.mention} joined the server",
                              colour=self.embed_colour)

            e.add_field(name="ID: ",
                        value=f"> {member.id}")

            e.set_thumbnail(url=f"{member.avatar_url}")

            e.set_footer(icon_url=f"{self.bot.user.avatar_url}")

            await self._des.send(embed=e)

            e = discord.Embed(title=f"Member Joined:",
                              description=f"{member.mention} joined the server",
                              colour=self.embed_colour)
            e.set_thumbnail(url=f"{member.avatar_url}")
            e.set_footer(icon_url=f"{self.bot.user.avatar_url}")

            await self.bot.get_guild(665743810315419670).get_channel(756698639585247355) \
                .send(content=f"<@&666738389407629333> please provide assistance",
                      embed=e)

        else:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == self.mod_channel_sc_id[0]:
            e = discord.Embed(title=f"Member Event:",
                              description=f"{member.mention} left the server",
                              colour=self.embed_colour)

            e.add_field(name="ID: ",
                        value=f"> {member.id}",
                        inline=True)

            join_date = member.joined_at - datetime.timedelta(microseconds=member.joined_at.microsecond)
            jd_differential = datetime.datetime.utcnow() - join_date

            e.add_field(name="Join Data:",
                        value=f"`{join_date}`", inline=False)

            e.set_thumbnail(url=f"{member.avatar_url}")

            e.set_footer(text=f"Time in server: {jd_differential}",
                         icon_url=f"{self.bot.user.avatar_url}")

            await self._des.send(embed=e)

        else:
            pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id == self.mod_channel_sc_id[0]:

            e = None
            mention = ""

            if before.channel is None:

                e = discord.Embed(title=f"Member Event:",
                                  description=f"{member.mention} joined a voice channel",
                                  colour=self.embed_colour)

                e.add_field(name="Channel: ",
                            value=f"> {after.channel.name}",
                            inline=True)

                e.set_thumbnail(url=f"{member.avatar_url}")

                e.set_footer(text=f"",
                             icon_url=f"{self.bot.user.avatar_url}")

                mention = f"<@242094224672161794>"

            elif after.channel is None:
                e = discord.Embed(title=f"Member Event:",
                                  description=f"{member.mention} left a voice channel",
                                  colour=self.embed_colour)

                e.add_field(name="Channel: ",
                            value=f"> {before.channel.name}",
                            inline=True)

                e.set_thumbnail(url=f"{member.avatar_url}")

                e.set_footer(text=f"",
                             icon_url=f"{self.bot.user.avatar_url}")

            if e is not None:
                await self._des.send(content=mention,
                                     embed=e)

        else:
            pass


def setup(bot):
    bot.add_cog(ModCog(bot))
    print("mod_lib has been loaded")
