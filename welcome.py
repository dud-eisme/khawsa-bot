import discord
import random
from discord.ext import commands

from variables import (
    MEMBER_ROLE, BOT_ROLE,
    WELCOME_FLAVOR_TEXTS, INTRO_FLAVOR_TEXTS,
    COLOR_FLAVOR_TEXTS, GENERAL_FLAVOR_TEXTS,
    AFTER_FLAVOR_TEXTS, BEFORE_FLAVOR_TEXTS,
    WELCOME_END_FLAVOR_TEXTS,
)
from channel_id import (
    WELCOME_CH, RULES_CH, INTRO_CH,
    COLOR_CH, TICKET_CH, GENERAL_CH,
    MEMBER_COUNT_CH,
)


async def update_member_count(guild):
    channel = guild.get_channel(MEMBER_COUNT_CH)
    role = discord.utils.get(guild.roles, name=MEMBER_ROLE)

    if channel and role:
        true_member_count = sum(1 for m in role.members if not m.bot)
        await channel.edit(name=f"📊 Surtis: {true_member_count}")
        print(f"📊 Verified Human Count: {true_member_count}")


class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            role = discord.utils.get(member.guild.roles, name=BOT_ROLE)
            if role:
                await member.add_roles(role)
                print("Bot")
            return

        role = discord.utils.get(member.guild.roles, name=MEMBER_ROLE)

        if role:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                print(f"Could not send DM to {member.name} or assign role.")

        await update_member_count(member.guild)

        welcome_ch = member.guild.get_channel(WELCOME_CH)
        rules_ch = member.guild.get_channel(RULES_CH)
        intro_ch = member.guild.get_channel(INTRO_CH)
        color_ch = member.guild.get_channel(COLOR_CH)
        ticket_ch = member.guild.get_channel(TICKET_CH)

        embed_private = discord.Embed(
            title=f"Welcome to r/surat!\n",
            color=0xc03843
        )

        embed_private.add_field(
            name="Step 1",
            value=f"📖 Rules {rules_ch.mention if rules_ch else '#rules'}",
            inline=False
        )

        embed_private.add_field(
            name="Step 2",
            value=f"👋 Introduction {intro_ch.mention if intro_ch else '#intro'}",
            inline=False
        )

        embed_private.add_field(
            name="Step 3",
            value=f"🎨 Color Roles {color_ch.mention if color_ch else '#colors'}",
            inline=False
        )

        embed_private.add_field(
            name="\u200b",
            value=f"> *Need help or have any suggestions? Just create a ticket at {ticket_ch.mention}*",
            inline=False
        )

        await member.send(content="", embed=embed_private)

        embed_server = discord.Embed(
            title=f"Welcome to r/surat, {member.name} 🧡\n",
            color=0xc03843
        )

        general_ch = member.guild.get_channel(GENERAL_CH)
        embed_server.add_field(
            name="\u200b",
            value=(
                f"{random.choice(WELCOME_FLAVOR_TEXTS)}\n"
                "\n"
                f"📖 Rules {rules_ch.mention if rules_ch else '#rules'}\n"
                f"📋 {random.choice(INTRO_FLAVOR_TEXTS)} {intro_ch.mention if intro_ch else '#intro'}\n"
                f"🎭 {random.choice(COLOR_FLAVOR_TEXTS)} {color_ch.mention if color_ch else '#colors'}\n"
                f"💬 {random.choice(GENERAL_FLAVOR_TEXTS)} {general_ch.mention if general_ch else '#general'}\n"
                "\n"
                f"{random.choice(WELCOME_END_FLAVOR_TEXTS)}"
            ),
            inline=False
        )

        await welcome_ch.send(
            content=f"{random.choice(BEFORE_FLAVOR_TEXTS)} {member.mention} {random.choice(AFTER_FLAVOR_TEXTS)}!",
            embed=embed_server
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await update_member_count(member.guild)


async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeCog(bot))
