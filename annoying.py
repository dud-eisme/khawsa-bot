import random
import asyncio
import time
import discord
from discord.ext import commands

from variables import MEMBER_ROLE, NVM_RESPONSES, UNHELPFUL_REPLIES, REACTION_EMOJIS


GHOST_PING_CHANCE = 0.01
FAKE_TYPING_CHANCE = 0.015
REACTION_SPAM_CHANCE = 0.02
DELAYED_REPLY_CHANCE = 0.015

GHOST_PING_COOLDOWN = 20 * 60
FAKE_TYPING_COOLDOWN = 20 * 60
REACTION_SPAM_COOLDOWN = 15 * 60
DELAYED_REPLY_COOLDOWN = 25 * 60


class AnnoyingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_ghost_ping = 0
        self.last_fake_typing = 0
        self.last_reaction_spam = 0
        self.last_delayed_reply = 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        now = time.time()

        if now - self.last_ghost_ping > GHOST_PING_COOLDOWN and random.random() < GHOST_PING_CHANCE:
            self.last_ghost_ping = now
            asyncio.create_task(self.ghost_ping(message))

        if now - self.last_fake_typing > FAKE_TYPING_COOLDOWN and random.random() < FAKE_TYPING_CHANCE:
            self.last_fake_typing = now
            asyncio.create_task(self.fake_typing(message))

        if now - self.last_reaction_spam > REACTION_SPAM_COOLDOWN and random.random() < REACTION_SPAM_CHANCE:
            self.last_reaction_spam = now
            asyncio.create_task(self.reaction_spam(message))

        if now - self.last_delayed_reply > DELAYED_REPLY_COOLDOWN and random.random() < DELAYED_REPLY_CHANCE:
            self.last_delayed_reply = now
            asyncio.create_task(self.delayed_reply(message))

    async def ghost_ping(self, message: discord.Message):
        role = discord.utils.get(message.guild.roles, name=MEMBER_ROLE)
        if not role:
            return

        human_members = [m for m in role.members if not m.bot]
        if not human_members:
            return

        target_user = random.choice(human_members)

        try:
            ghost_msg = await message.channel.send(f"{target_user.mention}")
            await ghost_msg.delete()
            print(f"👻 Ghost pinged {target_user.name} in #{message.channel.name}!")
        except discord.Forbidden:
            print("❌ Cannot ghost ping: Missing 'Send Messages' or 'Manage Messages' permission.")
        except Exception as e:
            print(f"❌ Ghost ping error: {e}")

    async def fake_typing(self, message: discord.Message):
        try:
            async with message.channel.typing():
                await asyncio.sleep(random.randint(20, 45))

            if random.random() < 0.5:
                await message.channel.send(random.choice(NVM_RESPONSES))
                print(f"⌨️ Fake typing resolved with a message in #{message.channel.name}.")
            else:
                print(f"⌨️ Fake typing resolved with... nothing in #{message.channel.name}.")
        except discord.Forbidden:
            print("❌ Cannot fake type: Missing 'Send Messages' permission.")
        except Exception as e:
            print(f"❌ Fake typing error: {e}")

    async def reaction_spam(self, message: discord.Message):
        try:
            emoji_count = random.randint(2, 5)
            chosen_emojis = random.sample(REACTION_EMOJIS, k=min(emoji_count, len(REACTION_EMOJIS)))

            for emoji in chosen_emojis:
                try:
                    await message.add_reaction(emoji)
                    await asyncio.sleep(random.uniform(0.3, 0.8))
                except discord.HTTPException:
                    continue

            print(f"🎭 Reaction-spammed {message.author.name}'s message with {len(chosen_emojis)} emojis.")
        except discord.Forbidden:
            print("❌ Cannot reaction spam: Missing 'Add Reactions' permission.")
        except Exception as e:
            print(f"❌ Reaction spam error: {e}")

    async def delayed_reply(self, message: discord.Message):
        try:
            await asyncio.sleep(47)
            await message.reply(random.choice(UNHELPFUL_REPLIES), mention_author=False)
            print(f"🐢 Sent a delayed unhelpful reply to {message.author.name}.")
        except discord.Forbidden:
            print("❌ Cannot delayed reply: Missing 'Send Messages' permission.")
        except Exception as e:
            print(f"❌ Delayed reply error: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(AnnoyingCog(bot))
