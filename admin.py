import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks

from variables import MOD_ROLES

# --- Admin Slash Commands ---

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="assign", description="Assign a role to a member")
    async def assign(self, interaction: discord.Interaction, assign_role: str, member: discord.Member = None):
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
    
    @app_commands.command(name="remove", description="Remove a role from a member")
    async def remove(self, interaction: discord.Interaction, remove_role: str, member: discord.Member = None):
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
            
    @app_commands.command(name="safai", description="Cleans up the specified number of messages from the channel")
    async def safai(self, interaction: discord.Interaction, amount: int = 10):
        if not any(role.name in MOD_ROLES for role in interaction.user.roles):
            await interaction.response.send_message(
                "You do not have the permissions to do that, baka!", 
                ephemeral=True
            )
            return
    
        await interaction.response.defer(ephemeral=True)
    
        try:
            deleted = await interaction.channel.purge(limit=amount)
            
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

    @app_commands.command(name="sync", description="Sync slash commands to this server")
    async def sync(self, interaction: discord.Interaction):
        if not any(role.name in MOD_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("You do not have the permissions to do that", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            synced = await self.bot.tree.sync(guild=discord.Object(id=interaction.guild.id))
            await interaction.followup.send(f"🔄 Synced {len(synced)} slash commands to this server.")
        except Exception as e:
            await interaction.followup.send(f"❌ Sync failed: {e}")



async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
