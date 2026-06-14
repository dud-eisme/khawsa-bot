import discord
from discord.ext import commands
from discord.ext import tasks
import logging
from dotenv import load_dotenv
import os
import random
import asyncio
from variables import MEMBER_ROLE
from channel_id import GUILD_ID, GENERAL_CH, OWNER_ID
from members import afk_reasons, save_afk_reasons
from welcome import update_member_count

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='UTF-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

greet_cooldowns = {}

#Bot Active Message
@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} is online!")

    guild = bot.get_guild(GUILD_ID)
    if guild:
        try:
            print(f"Requesting members for {guild.name}...")
            await guild.chunk(cache=True)
            print(f"Successfully chunked {guild.name}")
            await update_member_count(guild)
        except Exception as e:
            print(f"Chunking failed: {e}")
    
    activity = discord.Game(name="looking for Khawsa 🥣")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    if not rotate_custom_status.is_running():
        rotate_custom_status.start()

    if not random_ghost_ping.is_running():
        random_ghost_ping.start()

    # Sync Slash Commands Instantly to your local server
    try:
        # Pass your server ID as a discord.Object to bypass the global global delay
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"🔄 Immediate Sync: Updated {len(synced)} slash commands locally.")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

# --- Dynamic Custom Status Rotation ---
@tasks.loop(minutes=30)
async def rotate_custom_status():
    await bot.wait_until_ready()
    
    status_pool = [
        "my creator is so dumb 🤦‍♂️",
        "trying to fix creator's broken code... 🛠️",
        "coded by an absolute clown 🤡",
        "running on single-digit braincells today 🧠❌",
        "my creator thinks indentation is optional 😭",
        "stuck on a laptop because my dev is broke 🐧",
        "creator copy-pasted me from stackoverflow 📋🔧",
        "waiting for my dev to learn basic python 🐍📉",
        "my creator's code has more bugs than a swamp 🦟",
        "send help, my creator has no clue what they're doing SOS🆘"
    ]
    
    chosen_status = random.choice(status_pool)
    
    activity = discord.CustomActivity(name=f"{chosen_status}")
    
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"🔄 Status updated to: {chosen_status}")

# --- Random Ghost Ping Feature ---
@tasks.loop(minutes=30)  # Runs a check every 30 minutes
async def random_ghost_ping():
    await bot.wait_until_ready()
    
    # 🎲 40% chance to actually fire during this 30-minute interval to keep it unpredictable
    if random.random() > 0.40:
        return

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    # 🗣️ Target your main chat channel
    channel = guild.get_channel(GENERAL_CH)
    if not channel:
        return

    # Grab all non-bot members who are currently in the member role cache
    role = discord.utils.get(guild.roles, name=MEMBER_ROLE)
    if not role:
        return
        
    human_members = [m for m in role.members if not m.bot]
    
    if human_members:
        target_user = random.choice(human_members)
        
        try:
            # 👻 Send the ping
            ghost_msg = await channel.send(f"{target_user.mention}")
            # 💨 Vaporize it instantly!
            await ghost_msg.delete()
            print(f"👻 Ghost pinged {target_user.name} successfully in general!")
        except discord.Forbidden:
            print("❌ Cannot ghost ping: Missing 'Send Messages' or 'Manage Messages' permission.")
        except Exception as e:
            print(f"❌ Ghost ping error: {e}")

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
        save_afk_reasons(afk_reasons)
        
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

    # COMBINED TRIGGER: Catches "su chale", "shu chale", or a standalone/casual "hi"
    if "su chale" in msg or "shu chale" in msg:
        responses = [
            "Khawsa ni lari chale che, biju su!",
            "Bhagal par traffic chale che, bhai.",
            "Bas, tamari daya che!",
            "Dumas par bhoot chale che. 👻"
        ]
        await message.reply(random.choice(responses), mention_author=False)
        
        # 👋 CLEANED GREETING: Now ONLY triggers if the message starts with a greeting keyword or is exactly "hi"
    elif msg.startswith(("hello", "kem cho", "yo")) or msg.strip() == "hi":
        import time
        current_time = time.time()
        user_id = message.author.id
        
        # ⏱️ Check if the user is on a 5-minute (300 seconds) cooldown
        if user_id in greet_cooldowns and (current_time - greet_cooldowns[user_id]) < 300:
            return

        # If not on cooldown, update their timestamp and send the response
        greet_cooldowns[user_id] = current_time

        greeting_responses = [
            f"👋 *Aav baka aav!* Kem che {message.author.mention}?",
            f"🙌 *Yo bhura!* Su chale che? All good?",
            f"🥣 *Aao padharo!* Let's grab some hot Locho!",
            f"🍋 *Kem cho baka!* Bol su help joiye che?"
        ]
        await message.reply(random.choice(greeting_responses), mention_author=False)

    await bot.process_commands(message)   




#Bot Run Command
async def main():
    discord.utils.setup_logging(handler=handler, level=logging.DEBUG, root=False)
    async with bot:
        await bot.load_extension("admin")
        await bot.load_extension("members")
        await bot.load_extension("welcome")
        await bot.start(token)

asyncio.run(main())
