import discord
from discord.ext import commands
from discord.ext import tasks
import logging
from dotenv import load_dotenv
import os
import random
import asyncio
from channel_id import GUILD_ID, INTRO_CH
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

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"🔄 Immediate Sync: Updated {len(synced)} slash commands locally.")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

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

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.lower()

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

    if message.channel.id not in INTRO_CH:
        if "su chale" in msg or "shu chale" in msg:
            responses = [
                "Khawsa ni lari chale che, biju su!",
                "Bhagal par traffic chale che, bhai.",
                "Bas, tamari daya che!",
                "Dumas par bhoot chale che. 👻"
            ]
            await message.reply(random.choice(responses), mention_author=False)
            
        elif msg.startswith(("hello", "kem cho", "yo")) or msg.strip() == "hi":
            import time
            current_time = time.time()
            user_id = message.author.id
            
            if user_id in greet_cooldowns and (current_time - greet_cooldowns[user_id]) < 300:
                return
    
            greet_cooldowns[user_id] = current_time
    
            greeting_responses = [
                f"👋 *Aav baka aav!* Kem che {message.author.mention}?",
                f"🙌 *Yo bhura!* Su chale che? All good?",
                f"🥣 *Aao padharo!* Let's grab some hot Locho!",
                f"🍋 *Kem cho baka!* Bol su help joiye che?"
            ]
            await message.reply(random.choice(greeting_responses), mention_author=False)

    await bot.process_commands(message)   




async def main():
    discord.utils.setup_logging(handler=handler, level=logging.DEBUG, root=False)
    async with bot:
        await bot.load_extension("admin")
        await bot.load_extension("members")
        await bot.load_extension("welcome")
        await bot.load_extension("annoying")
        await bot.start(token)

asyncio.run(main())
