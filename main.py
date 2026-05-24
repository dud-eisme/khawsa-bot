from attr import define
import discord
from discord.ext import commands
from discord.ext import tasks
import logging
from dotenv import load_dotenv
import os
import random
import inspect
import feedparser
import re
import html
import asyncio
from variables import (
    MEMBER_ROLE, BOT_ROLE, MOD_ROLES, 
    WELCOME_FLAVOR_TEXTS, INTRO_FLAVOR_TEXTS, 
    COLOR_FLAVOR_TEXTS, GENERAL_FLAVOR_TEXTS,
    AFTER_FLAVOR_TEXTS, BEFORE_FLAVOR_TEXTS,
    WELCOME_END_FLAVOR_TEXTS, AFK_FLAVOR_TEXTS,
)
from channel_id import (
    GUILD_ID, WELCOME_CH, RULES_CH, INTRO_CH, 
    COLOR_CH, TICKET_CH, GENERAL_CH, 
    MEMBER_COUNT_CH, REDDIT_FEED_CH,
    OWNER_ID,
)
#import easter_eggs

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='UTF-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

afk_reasons = {}

#Bot Active Message
@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} is online!")

    # Sync Slash Commands Globally
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} slash commands globally.")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

    guild = bot.get_guild(GUILD_ID)
    if guild:
        try:
            print(f"Requesting members for {guild.name}...")
            await guild.chunk(cache=True)
            print(f"Successfully chunked {guild.name}")
            await update_member_count(guild)
        except Exception as e:
            print(f"Chunking failed: {e}")
    
    activity = discord.Activity(
        type=discord.ActivityType.listening, 
        name="looking for Khawsa 🥣"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

#On Join Activities
@bot.event
async def on_member_join(member):
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

    await asyncio.sleep(1)
    await update_member_count(member.guild)
            
    welcome_ch = member.guild.get_channel(WELCOME_CH)
    rules_ch = member.guild.get_channel(RULES_CH)
    intro_ch = member.guild.get_channel(INTRO_CH)
    color_ch = member.guild.get_channel(COLOR_CH)
    ticket_ch = member.guild.get_channel(TICKET_CH)

    embed_private = discord.Embed(
        title = f"Welcome to r/surat!\n",
        color = 0xc03843
    )
    
    embed_private.add_field(
        name = "Step 1",
        value = f"📖 Rules {rules_ch.mention if rules_ch else '#rules'}",
        inline = False
    )

    embed_private.add_field(
        name = "Step 2",
        value = f"👋 Introduction {intro_ch.mention if intro_ch else '#intro'}",
        inline = False
    )

    embed_private.add_field(
        name = "Step 3",
        value = f"🎨 Color Roles {color_ch.mention if color_ch else '#colors'}",
        inline = False
    )
    
    embed_private.add_field(
        name = "\u200b",
        value = f"> *Need help or have any suggestions? Just create a ticket at {ticket_ch.mention}*",
        inline = False
    )
            
    await member.send(content = "", embed = embed_private)
 
    embed_server = discord.Embed(
        title = f"Welcome to r/surat, {member.name} 🧡\n",
        color = 0xc03843
    )

    general_ch = member.guild.get_channel(GENERAL_CH)
    embed_server.add_field(
        name = "\u200b",
        value = (
            f"{random.choice(WELCOME_FLAVOR_TEXTS)}\n"
            "\n"
            f"📖 Rules {rules_ch.mention if rules_ch else '#rules'}\n"
            f"📋 {random.choice(INTRO_FLAVOR_TEXTS)} {intro_ch.mention if intro_ch else '#intro'}\n"
            f"🎭 {random.choice(COLOR_FLAVOR_TEXTS)} {color_ch.mention if color_ch else '#colors'}\n"
            f"💬 {random.choice(GENERAL_FLAVOR_TEXTS)} {general_ch.mention if general_ch else '#general'}\n"
            "\n"
            f"{random.choice(WELCOME_END_FLAVOR_TEXTS)}"
        ),
        inline = False
    )
    
    await welcome_ch.send(
        content = f"{random.choice(BEFORE_FLAVOR_TEXTS)} {member.mention} {random.choice(AFTER_FLAVOR_TEXTS)}!",
        embed = embed_server
    )
    
@bot.event
async def on_member_remove(member):
    await update_member_count(member.guild)

async def update_member_count(guild):
    channel_id = MEMBER_COUNT_CH
    channel = guild.get_channel(channel_id)
    role = discord.utils.get(guild.roles, name=MEMBER_ROLE)

    if channel and role:
        true_member_count = sum(1 for m in role.members if not m.bot)
        await channel.edit(name = f"📊 Members: {true_member_count}")
        print(f"📊 Verified Human Count: {true_member_count}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.lower()

    # --- AFK System ---
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
        
        if message.author.id == OWNER_ID and not status_removed:
            await message.reply(f"Welcome back, Boss! Tamara naam mathi [AFK] nathi hatavi saktu, permissions nathi ni! 🍋", delete_after=5, mention_author=False)
        else:
            await message.reply(f"Welcome back, I've removed your AFK status!", delete_after=5, mention_author=False)

    # --- Strict Empty Ping Detection ---
    if message.content.strip() == bot.user.mention:
        responses = [
            "Su kaam che baka? Kaam vagar magaj ni dahi nahi kar ni bura! 🤫",
            "Khali khali shu ping karya kare che? Lari par khawsa khava jav, mane hairan nahi kar! 🥣",
            "Oii bhura! Kaam ni vaat hoi to bol, nahi to dumas road par nikal chal! 😤",
            "Tamre potanu kai kaam nathi su? Shu @ khali khali thoka thok kare che! 🍋"
        ]
        await message.reply(random.choice(responses), mention_author=False)
        return

    if "khaman" in msg:
        if random.random() < 0.8: 
            await message.channel.send("Did someone say Khaman? Real Surtis know Locho is the goat. 🍋🥣")
            
    if "su chale" in msg or "shu chale" in msg:
        responses = [
            "Khawsa ni lari chale che, biju su!",
            "Bhagal par traffic chale che, bhai.",
            "Bas, tamari daya che!",
            "Dumas par bhoot chale che. 2"
        ]
        await message.reply(random.choice(responses), mention_author=False)
        
    if any(word in msg for word in ["hello", "hi", "kem cho"]) or msg.startswith("yo") or msg.startswith("hi"):
        await message.reply(f"👋 *Aav baka aav!* Kem che?", mention_author=False)
        
    elif any(word in msg for word in ["hungry", "bhookh", "dinner", "lunch", "food"]):
        await message.channel.send(
            "🍽️ *Bhaiyo*, if we are talking about food, it better be Surti Khawsa or Jaani's Locho. "
            "Don't suggest any weird items here, okay?"
        )

    await bot.process_commands(message)   

# --- Custom App (Slash) Commands ---

@bot.tree.command(name="hello", description="Checks if this was a command")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("was this a command?")

@bot.tree.command(name="afk", description="Sets your AFK status")
async def afk(interaction: discord.Interaction, reason: str = None):
    if reason is None:
        reason = random.choice(AFK_FLAVOR_TEXTS)
    target = interaction.user
    afk_reasons[interaction.user.id] = reason
    
    if not interaction.user.display_name.startswith("[AFK]"):
        try:
            await target.edit(nick=f"[AFK] {interaction.user.name}")
            await interaction.response.send_message(f"Your status is now AFK: **{reason}**")
        except discord.Forbidden:
            await interaction.response.send_message("I can't change your nickname, but I've noted you are AFK.")
    else:
        await interaction.response.send_message(f"AFK Reason updated: **{reason}**")

@bot.tree.command(name="kick", description="Try to kick a member from the server")
async def kick(interaction: discord.Interaction, member: discord.Member = None, reason: str = "No reason provided"):
    if member is None:
        await interaction.response.send_message("Kone kick karvu che, bhai? Name toh lakho! ✍️")
        return

    fake_kick_responses = [
        f"Tried to kick **{member.display_name}**, pan rasta ma traffic hatu toh pacha aai gaya. 🚦",
        f"**{member.display_name}** ne kick toh karwa gaya, pan rasta ma Locho ni lari dekhaai gai... bhuli gaya! 🍋🥣",
        f"Arey, **{member.display_name}** toh pappa na khas che. Emne nai kick karai, ni! 🤫",
        f"Bot is currently on a break at Dumas. Kick request rejected! 🌊👻",
        f"**{member.display_name}** pase 'VIP' pass che, Bhagal crossroads thi seedha entry mali gai! 🎟️",
        f"Kick fail! **{member.display_name}** is too heavy to kick after that heavy Gujarati Thali. 🍛😴"
    ]

    if member.id == OWNER_ID:
        await interaction.response.send_message(f"Watchman ne kick karwa niklo che? Pachha jao, thodu khawsa khai ne aao. 🥣🥣")
        return

    await interaction.response.send_message(random.choice(fake_kick_responses))

@bot.tree.command(name="ban", description="Try to ban a member from the server")
async def ban(interaction: discord.Interaction, member: discord.Member = None, reason: str = "No reason provided"):
    if member is None:
        await interaction.response.send_message("Kone ban karvu che? Khali fokat ma ban command nai vaparvani! 🚫")
        return

    fake_ban_responses = [
        f"**{member.display_name}** is banned from Surat! We put them on a bus to Ahmedabad, but they jumped off at Ankleshwar and came back. 🚌💨",
        f"Ban request for **{member.display_name}** rejected. They have an 'unlimited Locho' subscription at the local lari. 🍋🥣",
        f"System Error: **{member.display_name}** is too 'dhaba-dhaba' (strong) to be banned from this server. 💪",
        f"We tried to ban **{member.display_name}**, but they bribed the bot with a glass of A-One Cold Coco. 🍫🥤",
        f"**{member.display_name}** has been banned to the middle of the Tapi River. Update: They are currently swimming back. 🏊‍♂️🌉",
        f"Error 404: Ban hammer broken because **{member.display_name}** is a pure Surti diamond! 💎⚒️"
    ]

    if member.id == OWNER_ID:
        await interaction.response.send_message("Watchman ne ban karse toh aakha Surat ma tamaro ban thai jase, khabar che ne? 🤐")
        return
    
    if member.id == bot.user.id:
        await interaction.response.send_message("Mane ban karso toh tamaru setting kaun karse? Chalo, biju kaam karo! 🤖")
        return

    await interaction.response.send_message(random.choice(fake_ban_responses))

# Global command error handling remains for fallback/prefix infrastructure
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.reply("Avo koi command nathi baka! Slash command check karo slice slice!", mention_author=False)
        return

# --- Admin Slash Commands ---

@bot.tree.command(name="rules", description="Display server rules")
async def rules(interaction: discord.Interaction):
    # Check roles inside the interaction
    if not any(role.name in MOD_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("You do not have the permissions to do that", ephemeral=True)
        return

    embed = discord.Embed(title="RULES", color=0xc03843)
    embed.add_field(name="Promotion", value="Any kind of promotion/annoying links is/are prohibited.", inline=False)
    embed.add_field(
        name="Be Respectful to other Members", 
        value="Racism, Sexism are prohibited.\nPlease ask before DMing anyone.\nIf someone's not okay with something, stop. Please, just don't be a dick\n", 
        inline=False
    )
    embed.add_field(name="Discord TOS", value="Lastly, please follow Discord's TOS.", inline=False)

    await interaction.response.send_message(embed=embed)
    await interaction.channel.send(
        "**RULES**\n\n\n"
        "1. Any kind of promotion/annoying links is/are prohibited.\n\n"
        "2. Racism, Sexism are prohibited.\n\n"
        "3. Please ask before DMing anyone.\n\n"
        "4. Respect everyone's opinion. If someone is not okay with something, stop.\n\n"
        "5. Lastly, follow Discord's TOS.\n"
    )

@bot.tree.command(name="howto", description="Show the server operational guide")
async def howto(interaction: discord.Interaction):
    if not any(role.name in MOD_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("You do not have the permissions to do that", ephemeral=True)
        return

    content = inspect.cleandoc("""
        **How to use this server**
        If you’re new or confused, this will help you understand where to post what. No pressure to remember everything at once. Just start somewhere, you’ll figure it out over time.

        *Small reminder: this server only feels alive when people participate. Even small replies, reactions, or encouragement matter more than you think.*

        **Welcome Stuff**
        #🙂│welcome — You’ll see join messages here. No need to reply.
        #👋│intros — Introduce yourself. Reply to others too!
        #💜│colors — Pick a color role so your name looks nice.
        #🛡️│rules — Just don’t be weird. Be respectful.
        #📣│suno-suno-suno — Announcements & updates.

        **Casual & Community**
        #🗣️│general — Main chat. Start here.
        #🐢│general-slow — For a slower pace.
        #💬│serious — For proper, thoughtful discussions.
        #⭐│starboard — React with ⭐ to highlight great messages.
        #🎉│meetups-events — IRL meetups, movies, and VCs.

        Each plan in #🎉│meetups-events should go in its **own thread** so things don’t get messy.
    """)

    embed = discord.Embed(title="Server Guide 📖", description=content, color=0xf8c813)
    embed.set_footer(text="r/surat Community")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="assign", description="Assign a role to a member")
async def assign(interaction: discord.Interaction, assign_role: str, member: discord.Member = None):
    if not any(role.name in MOD_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("You do not have the permissions to do that", ephemeral=True)
        return

    member = member or interaction.user
    role = discord.utils.get(interaction.guild.roles, name=assign_role)
    if role:
        try: 
            await member.add_roles(role)
            await interaction.response.send_message(f"Successfully assigned {assign_role} to {member.display_name}")
        except discord.Forbidden:
            await interaction.response.send_message(f"I do not have the permissions to assign {assign_role}")
    else:
        await interaction.response.send_message(f"Role {assign_role} does not exist")

@bot.tree.command(name="remove", description="Remove a role from a member")
async def remove(interaction: discord.Interaction, remove_role: str, member: discord.Member = None):
    if not any(role.name in MOD_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("You do not have the permissions to do that", ephemeral=True)
        return

    member = member or interaction.user
    role = discord.utils.get(interaction.guild.roles, name=remove_role)
    if role:
        try:
            await member.remove_roles(role)
            await interaction.response.send_message(f"Successfully removed {remove_role} from {member.display_name}")
        except discord.Forbidden:
            await interaction.response.send_message("I do not have the permissions to remove this role")
    else:
        await interaction.response.send_message(f"User {member.name} does not have this role")
        
@bot.tree.command(name="safai", description="Cleans up the specified number of messages from the channel")
async def safai(interaction: discord.Interaction, amount: int = 10):
    # 1. Check if the user has a Moderator role
    if not any(role.name in MOD_ROLES for role in interaction.user.roles):
        await interaction.response.send_message(
            "You do not have the permissions to do that, baka!", 
            ephemeral=True
        )
        return

    # 2. Acknowledge the interaction immediately to prevent a timeout error
    # We use defer(ephemeral=True) so the "Thinking..." message is hidden from normal members
    await interaction.response.defer(ephemeral=True)

    try:
        # 3. Purge the messages from the channel
        # We add +1 if it were a text command, but for slash commands, the interaction doesn't count as a message!
        deleted = await interaction.channel.purge(limit=amount)
        
        # 4. Send the confirmation message inside the hidden ephemeral response
        await interaction.followup.send(
            f"🧹 Cleaned up {len(deleted)} messages from the chat, *bura*!"
        )
        
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ I don't have the `Manage Messages` permission in this channel!"
        )
    except Exception as e:
        await interaction.followup.send(
            f"❌ Something went wrong: {e}"
        )

#Bot Run Command
bot.run(token, log_handler=handler, log_level=logging.DEBUG)