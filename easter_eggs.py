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




handler = logging.FileHandler(filename='discord.log', encoding='UTF-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

afk_reasons = {}


#Hello Command
@bot.command()
async def hello(ctx):
    await ctx.send(f"was this a command?")


#AFK Tag
@bot.command()
async def afk(ctx, *, reason=random.choice(AFK_FLAVOR_TEXTS)):
    target = ctx.author
    afk_reasons[ctx.author.id] = reason
    if not ctx.author.display_name.startswith("[AFK]"):
        try:
            await target.edit(nick=f"[AFK] {ctx.author}")
        except discord.Forbidden:
            await ctx.send("I can't change your nickname, but I've noted you are AFK.")
    else:
        await ctx.send(f"AFK Reason: **{reason}**")
    print("Username changed.")
    
#AFK Remove Tag
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
        

    #AFK
    for mention in message.mentions:
        if mention.id in afk_reasons:
            reason = afk_reasons[mention.id]
            await message.channel.send(
                f"📌 {mention.display_name} is currently AFK: {reason}", 
                delete_after=10
            )
    
    if message.author.nick and message.author.nick.upper().startswith("[AFK] "):
        try:
            if message.author.nick and message.author.nick.upper().startswith("[AFK] "):
                new_nick = message.author.nick[6:]
                await message.author.edit(nick=new_nick)
            
            if message.author.id in afk_reasons:
                del afk_reasons[message.author.id]
                
            
        except discord.Forbidden:
            print(f"Permissions error: Could not change nick for {message.author.name}")
        except Exception as e:
            print(f"Error in AFK return: {e}")
            
        await message.channel.send(f"Welcome back {message.author.mention}, I've removed your AFK status!", delete_after=5)
            
    #Easter Eggs
    if "khaman" in message.content.lower():
        if random.random() < 0.4: 
            await message.channel.send("Did someone say Khaman? Real Surtis know Locho is the goat. 🍋🥣")
            
    if message.content.lower() == "su chale?":
        responses = [
            "Khawsa ni lari chale che, biju su!",
            "Bhagal par traffic chale che, bhai.",
            "Bas, tamari daya che!",
            "Dumas par bhoot chale che. 👻"
        ]
        await message.channel.send(random.choice(responses))
        
        
    await bot.process_commands(message)


#Pseudo Kick
@bot.command()
async def kick(ctx, member: discord.Member = None, *, reason="No reason provided"):
    if member is None:
        await ctx.send("Kone kick karvu che, bhai? Name toh lakho! ✍️")
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
        await ctx.send(f"Watchman ne kick karwa niklo che? Pachha jao, thodu khawsa khai ne aao. 🥣🥣")
        return

    await ctx.send(random.choice(fake_kick_responses))
    
#Pseudo Ban
@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason="No reason provided"):
    if member is None:
        await ctx.send("Kone ban karvu che? Khali fokat ma ban command nai vaparvani! 🚫")
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
        await ctx.send("Watchman ne ban karse toh aakha Surat ma tamaro ban thai jase, khabar che ne? 🤐")
        return
    
    if member.id == bot.user.id:
        await ctx.send("Mane ban karso toh tamaru setting kaun karse? Chalo, biju kaam karo! 🤖")
        return

    await ctx.send(random.choice(fake_ban_responses))
 