from Cogs.Package_Manual_Install import menus
import discord


# https://github.com/Rapptz/discord-ext-menus

# class MySource(menus.ListPageSource):
#
#     def format_page(self, menu, page):
#         if isinstance(page, str):
#             return page
#         else:
#
#             return '\n'.join(page)


# # in a command
# entries = ['a', 'b', 'c']
# source = MySource(entries, per_page=2)
# menu = menus.MenuPages(source)
# await menu.start(ctx)


class UserListSource(menus.ListPageSource):
    def __init__(self, data, user, embed_colour):
        super().__init__(data, per_page=5)
        self.user = user
        self.embed_colour = embed_colour

    async def format_page(self, menu, entries):

        e = discord.Embed(title="Reminders:",
                          colour=self.embed_colour)

        if len(entries) != 0:
            res_str = ""
            for r in entries:
                res_str += str(r.rem_id) + ". " + str(r)
                res_str += "\n"

                e.add_field(name=f"ID: {r.rem_id}",
                            value=str(r),
                            inline=False)

            e.set_footer(icon_url=str(self.user.avatar_url),
                         text=f"Reminders for {self.user.name}")

        else:
            e = discord.Embed(title="No Reminders Present :)", colour=self.embed_colour)
            e.set_footer(icon_url=str(self.user.avatar_url),
                         text=f"Reminders for {self.user.name}")

        return e


# # somewhere else in command:
# pages = menus.MenuPages(source=MySource2(range(1, 100)), clear_reactions_after=True)
# await pages.start(ctx)


class AllListSource(menus.ListPageSource):
    def __init__(self, data, bot, embed_colour):
        super().__init__(data, per_page=5)
        self.bot = bot
        self.embed_colour = embed_colour

    async def format_page(self, menu, entries):

        e = discord.Embed(title="Reminders:",
                          colour=self.embed_colour)

        if len(entries) != 0:
            res_str = ""
            for r in entries:
                user = self.bot.get_user(r.user_bind)

                res_str += str(r.rem_id) + ". " + str(r)
                res_str += "\n"

                e.add_field(name=f"ID: {r.rem_id} by {user.name}#{user.discriminator} : {user.id}",
                            value=str(r),
                            inline=False)

            e.set_footer(text=f"Reminders for all users")

        else:
            e = discord.Embed(title="No Reminders Present :)", colour=self.embed_colour)
            e.set_footer(text=f"Reminders for all users")

        return e
