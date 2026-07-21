import random
import os
import json
import discord
from discord import app_commands
from discord.ext import commands

from channel_id import OWNER_ID

from variables import AFK_FLAVOR_TEXTS

AFK_FILE = "afk_reasons.json"

def load_afk_reasons() -> dict:
    if not os.path.exists(AFK_FILE):
        return {}
    try:
        with open(AFK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    except (json.JSONDecodeError, ValueError):
        return {}


def save_afk_reasons(afk_reasons: dict):
    with open(AFK_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in afk_reasons.items()}, f, indent=2)


afk_reasons = load_afk_reasons()

class MemberCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        for mention in message.mentions:
            if mention.id in afk_reasons:
                reason = afk_reasons[mention.id]
                await message.channel.send(
                    f"📌 {mention.display_name} is currently AFK: {reason}",
                    delete_after=10
                )

        if message.author.id in afk_reasons:
            status_removed = False

            if message.author.nick and message.author.nick.upper().startswith("[AFK]"):
                new_nick = message.author.nick[6:].strip()
                try:
                    await message.author.edit(nick=new_nick)
                    status_removed = True
                except discord.Forbidden:
                    if message.author.id == OWNER_ID:
                        print(f"Owner detected. Skipping nick change for {message.author.name}")
                    else:
                        print(f"Permissions error: Role hierarchy issue with {message.author.name}")

            del afk_reasons[message.author.id]
            save_afk_reasons(afk_reasons)

            if message.author.id == OWNER_ID and not status_removed:
                await message.reply(f"Welcome back, Boss! Tamara naam mathi [AFK] nathi hatavi saktu, permissions nathi ni! 🍋", delete_after=5, mention_author=False)
            else:
                await message.reply(f"Welcome back, I've removed your AFK status!", delete_after=5, mention_author=False)

    @app_commands.command(name="hello", description="Checks if this was a command")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("was this a command?")
    
    @app_commands.command(name="afk", description="Sets your AFK status")
    async def afk(self, interaction: discord.Interaction, reason: str = None):
        if reason is None:
            reason = random.choice(AFK_FLAVOR_TEXTS)
        target = interaction.user
        afk_reasons[interaction.user.id] = reason
        save_afk_reasons(afk_reasons)
        
        if not interaction.user.display_name.startswith("[AFK]"):
            try:
                await target.edit(nick=f"[AFK] {interaction.user.name}")
                await interaction.response.send_message(f"Your status is now AFK: **{reason}**")
            except discord.Forbidden:
                await interaction.response.send_message("I can't change your nickname, but I've noted you are AFK.")
        else:
            await interaction.response.send_message(f"AFK Reason updated: **{reason}**")

    @app_commands.command(name="kick", description="Kick a member from the server")
    async def kick(self, interaction: discord.Interaction, member: discord.Member = None, reason: str = "No reason provided"):
        if member is None:
            await interaction.response.send_message("Kone kick karvu che, bhai? Name toh lakho! ✍️", ephemeral=True)
            return
    
        if member.id == OWNER_ID:
            await interaction.response.send_message("You cannot kick the Boss! 🍋", ephemeral=True)
            return
    
        if member.id == self.bot.user.id:
            await interaction.response.send_message("Mane kick karso toh tamaru setting kaun karse? Chal nikal! 🤖", ephemeral=True)
            return
    
        kick_lines = [
            f"Tried to kick **{member.display_name}**, pan rasta ma traffic hatu toh pacha aai gaya. 🚦",
            f"**{member.display_name}** ne kick toh karwa gaya, pan rasta ma Locho ni lari dekhaai gai... bhuli gaya! 🍋🥣",
            f"Arey, **{member.display_name}** toh pappa na khas che. Emne nai kick karai, ni! 🤫",
            f"Bot is currently on a break at Dumas. Kick request rejected! 🌊👻",
            f"**{member.display_name}** pase 'VIP' pass che, Bhagal crossroads thi seedha entry mali gai! 🎟️",
            f"Kick fail! **{member.display_name}** is too heavy to kick after that heavy Gujarati Thali. 🍛😴",
        ]
        await interaction.response.send_message(random.choice(kick_lines))
    
    @app_commands.command(name="ban", description="Ban a member from the server")
    async def ban(self, interaction: discord.Interaction, member: discord.Member = None, reason: str = "No reason provided"):
        if member is None:
            await interaction.response.send_message("Kone ban karvu che? Khali fokat ma ban command nai vaparvani! 🚫", ephemeral=True)
            return
    
        if member.id == OWNER_ID:
            await interaction.response.send_message("Watchman ne ban karse toh aakha Surat ma tamaro ban thai jase! 🤐", ephemeral=True)
            return
        
        if member.id == self.bot.user.id:
            await interaction.response.send_message("Mane ban karso toh tame ahiya locho vechva baiso su? Chalo, biju kaam karo! 🤖", ephemeral=True)
            return
    
        ban_lines = [
            f"**{member.display_name}** is banned from Surat! We put them on a bus to Ahmedabad, but they jumped off at Ankleshwar and came back. 🚌💨",
            f"Ban request for **{member.display_name}** rejected. They have an 'unlimited Locho' subscription at the local lari. 🍋🥣",
            f"System Error: **{member.display_name}** is too 'dhaba-dhaba' (strong) to be banned from this server. 💪",
            f"We tried to ban **{member.display_name}**, but they bribed the bot with a glass of A-One Cold Coco. 🍫🥤",
            f"**{member.display_name}** has been banned to the middle of the Tapi River. Update: They are currently swimming back. 🏊‍♂️🌉",
            f"Error 404: Ban hammer broken because **{member.display_name}** is a pure Surti diamond! 💎⚒️",
        ]
        await interaction.response.send_message(random.choice(ban_lines))



async def setup(bot: commands.Bot):
    await bot.add_cog(MemberCog(bot))
