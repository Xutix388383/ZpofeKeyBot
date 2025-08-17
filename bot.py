
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import secrets
import string
import time
from datetime import datetime, timedelta
import asyncio
from flask import Flask, request, jsonify, render_template_string
import threading

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Flask app for webhook endpoints and frontend
app = Flask(__name__)

# Key storage file
KEYS_FILE = "keys.json"
USERS_FILE = "users.json"
SCRIPTS_FILE = "scripts.json"
HWID_COOLDOWNS_FILE = "hwid_cooldowns.json"

# Required role IDs
BUYER_ROLE_ID = 1406653314589786204
STAFF_ROLE_ID = 1399949855799119952

# Load or create storage files
def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_scripts():
    if os.path.exists(SCRIPTS_FILE):
        with open(SCRIPTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_scripts(scripts):
    with open(SCRIPTS_FILE, 'w') as f:
        json.dump(scripts, f, indent=2)

def load_hwid_cooldowns():
    if os.path.exists(HWID_COOLDOWNS_FILE):
        with open(HWID_COOLDOWNS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_hwid_cooldowns(cooldowns):
    with open(HWID_COOLDOWNS_FILE, 'w') as f:
        json.dump(cooldowns, f, indent=2)

# Generate random key
def generate_key():
    return "ZPOFES-" + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))

def generate_script_id():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))

# Bot events
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Webhook server will run on http://0.0.0.0:5000')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Staff Panel Command (Public panel, private button responses for staff)
@bot.tree.command(name="staffpanel", description="Open the ZpofeHub staff panel")
async def staff_panel(interaction: discord.Interaction):
    """Staff panel command - public panel with private button responses for staff"""
    
    embed = discord.Embed(
        title="🚀 ZpofeHub Staff Panel",
        description="Professional staff control panel for managing ZpofeHub infrastructure",
        color=0x6a0dad,
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="📊 Dashboard Analytics",
        value="View comprehensive system statistics and performance metrics",
        inline=False
    )

    embed.add_field(
        name="🔑 License Management", 
        value="Generate, monitor, and manage all license keys in the system",
        inline=False
    )

    embed.add_field(
        name="📝 Script Administration",
        value="Upload, configure, and monitor protected script deployments",
        inline=False
    )

    embed.add_field(
        name="⚙️ System Configuration",
        value="Manage system settings, security policies, and API configurations",
        inline=False
    )

    embed.add_field(
        name="ℹ️ Staff Access Required",
        value="Click any button below to access staff-only administrative features",
        inline=False
    )

    embed.set_footer(text="ZpofeHub Staff Panel • Staff role required for access")

    view = StaffPanelView()
    await interaction.response.send_message(embed=embed, view=view)

# User Panel Command (Public panel, private button responses)
@bot.tree.command(name="userpanel", description="Access your ZpofeHub user panel")
async def user_panel(interaction: discord.Interaction):
    """User panel command - public panel with private button responses"""
    
    embed = discord.Embed(
        title="👑 ZpofeHub User Panel",
        description="Welcome to ZpofeHub - Your gateway to premium scripts and license management",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="🔑 License Key Access",
        value="Get your working license key for purchased scripts",
        inline=False
    )

    embed.add_field(
        name="📜 Get Script",
        value="Get your premium script loadstring via DM",
        inline=False
    )

    embed.add_field(
        name="⚙️ Settings",
        value="Manage your account settings and reset HWID",
        inline=False
    )

    embed.add_field(
        name="ℹ️ Information",
        value="Click any button below to access your personal dashboard features",
        inline=False
    )
    
    embed.set_footer(text="ZpofeHub User Panel • Click buttons for private access")

    view = UserPanelView()
    await interaction.response.send_message(embed=embed, view=view)

# Custom Views for Interactive Panels
class StaffPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="📊 Dashboard", style=discord.ButtonStyle.primary, emoji="📊")
    async def dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has staff role for access
        staff_role = discord.utils.get(interaction.guild.roles, id=STAFF_ROLE_ID)
        has_staff_role = staff_role in interaction.user.roles
        
        if not has_staff_role:
            embed = discord.Embed(
                title="❌ Access Denied",
                description=f"You need the {staff_role.name if staff_role else 'Staff'} role to access the dashboard.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await show_dashboard(interaction)

    @discord.ui.button(label="🔑 Keys", style=discord.ButtonStyle.secondary, emoji="🔑")
    async def keys(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has staff role for access
        staff_role = discord.utils.get(interaction.guild.roles, id=STAFF_ROLE_ID)
        has_staff_role = staff_role in interaction.user.roles
        
        if not has_staff_role:
            embed = discord.Embed(
                title="❌ Access Denied",
                description=f"You need the {staff_role.name if staff_role else 'Staff'} role to access key management.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await show_key_management(interaction)

    @discord.ui.button(label="📝 Scripts", style=discord.ButtonStyle.secondary, emoji="📝")
    async def scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has staff role for access
        staff_role = discord.utils.get(interaction.guild.roles, id=STAFF_ROLE_ID)
        has_staff_role = staff_role in interaction.user.roles
        
        if not has_staff_role:
            embed = discord.Embed(
                title="❌ Access Denied",
                description=f"You need the {staff_role.name if staff_role else 'Staff'} role to access script management.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await show_script_management(interaction)

    @discord.ui.button(label="⚙️ Settings", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has staff role for access
        staff_role = discord.utils.get(interaction.guild.roles, id=STAFF_ROLE_ID)
        has_staff_role = staff_role in interaction.user.roles
        
        if not has_staff_role:
            embed = discord.Embed(
                title="❌ Access Denied",
                description=f"You need the {staff_role.name if staff_role else 'Staff'} role to access settings.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await show_settings(interaction)

class KeyManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🆕 Generate Key", style=discord.ButtonStyle.success, emoji="🆕")
    async def generate_key_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_key_generation(interaction)

    @discord.ui.button(label="📋 List Keys", style=discord.ButtonStyle.primary, emoji="📋")
    async def list_keys(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_key_list(interaction)

    @discord.ui.button(label="🔍 Key Info", style=discord.ButtonStyle.secondary, emoji="🔍")
    async def key_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = KeyInfoModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🗑️ Delete Key", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_key(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DeleteKeyModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary, emoji="🔙")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = StaffPanelView()
        embed = discord.Embed(
            title="🚀 ZpofeHub Staff Panel",
            description="Select an option from the menu below",
            color=0x6a0dad
        )
        await interaction.response.edit_message(embed=embed, view=view)

class ScriptManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="📤 Upload Script", style=discord.ButtonStyle.success, emoji="📤")
    async def upload_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = UploadScriptModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="📋 List Scripts", style=discord.ButtonStyle.primary, emoji="📋")
    async def list_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_script_list(interaction)

    @discord.ui.button(label="📊 Analytics", style=discord.ButtonStyle.secondary, emoji="📊")
    async def analytics(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_analytics(interaction)

    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary, emoji="🔙")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = StaffPanelView()
        embed = discord.Embed(
            title="🚀 ZpofeHub Staff Panel",
            description="Select an option from the menu below",
            color=0x6a0dad
        )
        await interaction.response.edit_message(embed=embed, view=view)

# User Settings View
class UserSettingsView(discord.ui.View):
    def __init__(self, on_cooldown=False):
        super().__init__(timeout=300)
        self.on_cooldown = on_cooldown

    @discord.ui.button(label="🔄 Reset HWID", style=discord.ButtonStyle.danger, emoji="🔄")
    async def reset_hwid_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.on_cooldown:
            embed = discord.Embed(
                title="❌ Cooldown Active",
                description="You can only reset your HWID once every 24 hours.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await reset_user_hwid(interaction)

    @discord.ui.button(label="📊 Account Info", style=discord.ButtonStyle.secondary, emoji="📊")
    async def account_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📊 Account Information",
            description="Your ZpofeHub account details",
            color=0x6a0dad,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 Username", value=interaction.user.display_name, inline=True)
        embed.add_field(name="🆔 User ID", value=str(interaction.user.id), inline=True)
        embed.add_field(name="✅ Status", value="Premium User", inline=True)
        embed.add_field(name="📅 Joined", value=interaction.user.joined_at.strftime("%Y-%m-%d"), inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def reset_user_hwid(interaction):
    """Reset user's HWID with cooldown check"""
    user_id = str(interaction.user.id)
    cooldowns = load_hwid_cooldowns()
    
    # Check cooldown
    if user_id in cooldowns:
        last_reset = cooldowns[user_id]
        if time.time() - last_reset < 86400:  # 24 hours
            cooldown_remaining = 86400 - (time.time() - last_reset)
            hours = int(cooldown_remaining // 3600)
            minutes = int((cooldown_remaining % 3600) // 60)
            
            embed = discord.Embed(
                title="❌ Cooldown Active",
                description=f"You can reset your HWID again in {hours}h {minutes}m.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    
    # Find and reset user's key HWID
    keys = load_keys()
    user_key = None
    
    for key, data in keys.items():
        if data.get("owner") == user_id:
            user_key = key
            break
    
    if not user_key:
        embed = discord.Embed(
            title="❌ No Key Found",
            description="You don't have a license key to reset.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Reset HWID
    keys[user_key]["hwid"] = None
    keys[user_key]["used"] = False
    save_keys(keys)
    
    # Set cooldown
    cooldowns[user_id] = time.time()
    save_hwid_cooldowns(cooldowns)
    
    embed = discord.Embed(
        title="✅ HWID Reset",
        description="Your HWID has been successfully reset! You can now use your key on a different device.",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="⏰ Next Reset", value="Available in 24 hours", inline=True)
    embed.set_footer(text="Your key is now unbound from any hardware")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# User Panel Functions
class UserPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🔑 Get My Key", style=discord.ButtonStyle.success, emoji="🔑")
    async def get_my_key(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has buyer role for access
        buyer_role = discord.utils.get(interaction.guild.roles, id=BUYER_ROLE_ID)
        has_buyer_role = buyer_role in interaction.user.roles
        
        if not has_buyer_role:
            embed = discord.Embed(
                title="❌ Access Denied",
                description=f"You need the {buyer_role.name if buyer_role else 'Buyer'} role to access your license key.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await show_user_key(interaction)

    @discord.ui.button(label="📜 Get Script", style=discord.ButtonStyle.primary, emoji="📜")
    async def get_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has buyer role for access
        buyer_role = discord.utils.get(interaction.guild.roles, id=BUYER_ROLE_ID)
        has_buyer_role = buyer_role in interaction.user.roles
        
        if not has_buyer_role:
            embed = discord.Embed(
                title="❌ Access Denied",
                description=f"You need the {buyer_role.name if buyer_role else 'Buyer'} role to get the script.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await send_script_dm(interaction)

    @discord.ui.button(label="⚙️ Settings", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has buyer role for access
        buyer_role = discord.utils.get(interaction.guild.roles, id=BUYER_ROLE_ID)
        has_buyer_role = buyer_role in interaction.user.roles
        
        if not has_buyer_role:
            embed = discord.Embed(
                title="❌ Access Denied",
                description=f"You need the {buyer_role.name if buyer_role else 'Buyer'} role to access settings.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await show_user_settings(interaction)

async def show_user_key(interaction):
    """Show the user's working license key"""
    user_id = str(interaction.user.id)
    keys = load_keys()
    
    # Find user's key
    user_key = None
    for key, data in keys.items():
        if data.get("owner") == user_id:
            user_key = key
            break
    
    if not user_key:
        # Generate a new key for the user
        user_key = generate_key()
        keys[user_key] = {
            "type": "perm",
            "owner": user_id,
            "created_at": time.time(),
            "expires_at": None,
            "hwid": None,
            "used": False
        }
        save_keys(keys)
    
    embed = discord.Embed(
        title="🔑 Your License Key",
        description="Here is your working license key for ZpofeHub",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="🔑 License Key", value=f"`{user_key}`", inline=False)
    embed.add_field(name="✅ Status", value="Active", inline=True)
    embed.add_field(name="📅 Type", value="Permanent", inline=True)
    embed.add_field(name="💻 HWID", value="Not bound" if not keys[user_key]["hwid"] else "Bound", inline=True)
    
    embed.set_footer(text="Keep this key safe and secure!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def send_script_dm(interaction):
    """Send script loadstring via DM"""
    try:
        # Create DM embed
        embed = discord.Embed(
            title="📜 Your ZpofeHub Script",
            description="Here is your premium script loadstring:",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔗 Script Loadstring",
            value="```lua\nloadstring(game:HttpGet(\"https://pastebin.com/raw/DmRu7yE0\"))()```",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Instructions",
            value="Copy and paste this loadstring into your executor to run the script.",
            inline=False
        )
        
        embed.set_footer(text="ZpofeHub - Premium Scripts")
        
        # Send DM
        await interaction.user.send(embed=embed)
        
        # Confirm in channel
        confirm_embed = discord.Embed(
            title="✅ Script Sent",
            description="Your script loadstring has been sent to your DMs!",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
        
    except discord.Forbidden:
        # User has DMs disabled
        embed = discord.Embed(
            title="❌ DM Failed",
            description="Unable to send DM. Please enable DMs from server members and try again.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def show_user_settings(interaction):
    """Show user settings with HWID reset option"""
    cooldowns = load_hwid_cooldowns()
    user_id = str(interaction.user.id)
    
    # Check if user has HWID reset cooldown
    cooldown_remaining = 0
    if user_id in cooldowns:
        last_reset = cooldowns[user_id]
        cooldown_remaining = max(0, 86400 - (time.time() - last_reset))  # 24 hours = 86400 seconds
    
    embed = discord.Embed(
        title="⚙️ Settings",
        description="Manage your ZpofeHub account settings",
        color=0x6a0dad,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="👤 Username", value=interaction.user.display_name, inline=True)
    embed.add_field(name="🆔 User ID", value=str(interaction.user.id), inline=True)
    embed.add_field(name="✅ Status", value="Premium User", inline=True)
    
    if cooldown_remaining > 0:
        hours = int(cooldown_remaining // 3600)
        minutes = int((cooldown_remaining % 3600) // 60)
        embed.add_field(
            name="⏰ HWID Reset Cooldown", 
            value=f"{hours}h {minutes}m remaining", 
            inline=False
        )
    else:
        embed.add_field(
            name="🔄 HWID Reset", 
            value="Available - Click button below to reset", 
            inline=False
        )
    
    view = UserSettingsView(cooldown_remaining > 0)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Modal Classes for Input
class KeyInfoModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="🔍 Key Information")

    key = discord.ui.TextInput(
        label="License Key",
        placeholder="Enter the license key to check...",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        keys = load_keys()
        key_value = self.key.value.strip()

        if key_value not in keys:
            embed = discord.Embed(
                title="❌ Key Not Found",
                description=f"The key `{key_value}` was not found in the database.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        key_data = keys[key_value]

        embed = discord.Embed(
            title="🔍 Key Information",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="🔑 Key", value=f"`{key_value}`", inline=False)
        embed.add_field(name="📋 Type", value=key_data["type"].title(), inline=True)
        embed.add_field(name="✅ Used", value="Yes" if key_data["used"] else "No", inline=True)

        if key_data["hwid"]:
            embed.add_field(name="💻 HWID", value=f"`{key_data['hwid'][:20]}...`", inline=False)

        created_time = datetime.fromtimestamp(key_data["created_at"])
        embed.add_field(name="📅 Created", value=created_time.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

        if key_data["expires_at"]:
            expires_time = datetime.fromtimestamp(key_data["expires_at"])
            embed.add_field(name="⏰ Expires", value=expires_time.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

            if time.time() > key_data["expires_at"]:
                embed.add_field(name="🔴 Status", value="Expired", inline=True)
            else:
                embed.add_field(name="🟢 Status", value="Active", inline=True)
        else:
            embed.add_field(name="🟢 Status", value="Active (Permanent)", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

class DeleteKeyModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="🗑️ Delete Key")

    key = discord.ui.TextInput(
        label="License Key",
        placeholder="Enter the license key to delete...",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Check staff role
        staff_role = discord.utils.get(interaction.guild.roles, id=STAFF_ROLE_ID)
        if staff_role not in interaction.user.roles:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need staff permissions to delete keys.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        keys = load_keys()
        key_value = self.key.value.strip()

        if key_value in keys:
            del keys[key_value]
            save_keys(keys)

            embed = discord.Embed(
                title="✅ Key Deleted",
                description=f"Key `{key_value}` has been successfully deleted.",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="❌ Key Not Found",
                description=f"The key `{key_value}` was not found in the database.",
                color=0xff0000
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

class UploadScriptModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="📤 Upload Script")

    name = discord.ui.TextInput(
        label="Script Name",
        placeholder="Enter script name...",
        required=True,
        max_length=100
    )

    description = discord.ui.TextInput(
        label="Description",
        placeholder="Enter script description...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        scripts = load_scripts()
        script_id = generate_script_id()

        scripts[script_id] = {
            "name": self.name.value,
            "description": self.description.value or "No description provided",
            "owner": str(interaction.user.id),
            "created_at": time.time(),
            "downloads": 0,
            "executions": 0
        }

        save_scripts(scripts)

        embed = discord.Embed(
            title="✅ Script Uploaded",
            description=f"Script **{self.name.value}** has been uploaded successfully!",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="📋 Script ID", value=f"`{script_id}`", inline=True)
        embed.add_field(name="👤 Owner", value=interaction.user.mention, inline=True)
        embed.add_field(name="📝 Description", value=self.description.value or "No description", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

# Staff Panel Functions
async def show_dashboard(interaction):
    keys = load_keys()
    scripts = load_scripts()
    users = load_users()

    total_keys = len(keys)
    active_keys = sum(1 for k in keys.values() if not k.get("expires_at") or time.time() < k["expires_at"])
    total_scripts = len(scripts)
    total_users = len(users)

    embed = discord.Embed(
        title="📊 Dashboard Overview",
        description="Your ZpofeHub statistics and overview",
        color=0x6a0dad,
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🔑 Total Keys", value=str(total_keys), inline=True)
    embed.add_field(name="✅ Active Keys", value=str(active_keys), inline=True)
    embed.add_field(name="📝 Scripts", value=str(total_scripts), inline=True)
    embed.add_field(name="👥 Users", value=str(total_users), inline=True)
    embed.add_field(name="⚡ Status", value="🟢 Online", inline=True)
    embed.add_field(name="🔄 Uptime", value="99.9%", inline=True)

    view = StaffPanelView()
    await interaction.response.edit_message(embed=embed, view=view)

async def show_key_management(interaction):
    embed = discord.Embed(
        title="🔑 Key Management",
        description="Manage your license keys and access controls",
        color=0x6a0dad,
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="🆕 Generate Key",
        value="Create new temporary or permanent keys",
        inline=False
    )

    embed.add_field(
        name="📋 List Keys",
        value="View all existing keys and their status",
        inline=False
    )

    embed.add_field(
        name="🔍 Key Information",
        value="Get detailed information about a specific key",
        inline=False
    )

    view = KeyManagementView()
    await interaction.response.edit_message(embed=embed, view=view)

async def show_script_management(interaction):
    embed = discord.Embed(
        title="📝 Script Management",
        description="Upload, manage, and monitor your protected scripts",
        color=0x6a0dad,
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="📤 Upload Script",
        value="Upload a new script to the protection system",
        inline=False
    )

    embed.add_field(
        name="📋 Script Library",
        value="View all uploaded scripts and their statistics",
        inline=False
    )

    embed.add_field(
        name="📊 Analytics",
        value="View execution statistics and usage data",
        inline=False
    )

    view = ScriptManagementView()
    await interaction.response.edit_message(embed=embed, view=view)

async def show_settings(interaction):
    embed = discord.Embed(
        title="⚙️ Settings & Configuration",
        description="Configure your ZpofeHub panel settings",
        color=0x6a0dad,
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="🔧 API Configuration",
        value="Configure webhook endpoints and API settings",
        inline=False
    )

    embed.add_field(
        name="🛡️ Security Settings",
        value="Manage HWID restrictions and security policies",
        inline=False
    )

    embed.add_field(
        name="📬 Notifications",
        value="Configure alerts and notification preferences",
        inline=False
    )

    view = StaffPanelView()
    await interaction.response.edit_message(embed=embed, view=view)

async def show_key_generation(interaction):
    # Check staff role
    staff_role = discord.utils.get(interaction.guild.roles, id=STAFF_ROLE_ID)
    if staff_role not in interaction.user.roles:
        embed = discord.Embed(
            title="❌ Access Denied",
            description="You need staff permissions to generate keys.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    key = generate_key()
    keys = load_keys()

    keys[key] = {
        "type": "perm",
        "created_by": str(interaction.user.id),
        "created_at": time.time(),
        "expires_at": None,
        "hwid": None,
        "used": False,
        "owner": None
    }

    save_keys(keys)

    embed = discord.Embed(
        title="🔑 Key Generated Successfully",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🔑 New Key", value=f"`{key}`", inline=False)
    embed.add_field(name="⏰ Duration", value="Permanent", inline=True)
    embed.add_field(name="📅 Type", value="Staff Generated", inline=True)
    embed.set_footer(text=f"Generated by {interaction.user}")

    await interaction.response.send_message(embed=embed, ephemeral=True)

async def show_key_list(interaction):
    keys = load_keys()

    if not keys:
        embed = discord.Embed(
            title="📝 No Keys Found",
            description="No license keys have been generated yet.",
            color=0xff9900
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="📋 License Keys Overview",
        color=0x6a0dad,
        timestamp=datetime.utcnow()
    )

    for i, (key, data) in enumerate(list(keys.items())[:5]):  # Show first 5 keys
        status = "🔴 Expired" if data.get("expires_at") and time.time() > data["expires_at"] else "🟢 Active"
        used = "✅ Used" if data["used"] else "❌ Unused"

        embed.add_field(
            name=f"`{key[:15]}...`",
            value=f"**Type:** {data['type']}\n**Status:** {status}\n**Used:** {used}",
            inline=True
        )

    if len(keys) > 5:
        embed.set_footer(text=f"Showing 5 of {len(keys)} keys")

    await interaction.response.send_message(embed=embed, ephemeral=True)

async def show_script_list(interaction):
    scripts = load_scripts()

    if not scripts:
        embed = discord.Embed(
            title="📝 No Scripts Found",
            description="No scripts have been uploaded yet.",
            color=0xff9900
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="📋 Script Library",
        color=0x6a0dad,
        timestamp=datetime.utcnow()
    )

    for script_id, data in list(scripts.items())[:5]:  # Show first 5 scripts
        embed.add_field(
            name=f"📄 {data['name']}",
            value=f"**ID:** `{script_id}`\n**Downloads:** {data['downloads']}\n**Executions:** {data['executions']}",
            inline=True
        )

    if len(scripts) > 5:
        embed.set_footer(text=f"Showing 5 of {len(scripts)} scripts")

    await interaction.response.send_message(embed=embed, ephemeral=True)

async def show_analytics(interaction):
    scripts = load_scripts()
    keys = load_keys()

    total_executions = sum(script.get('executions', 0) for script in scripts.values())
    total_downloads = sum(script.get('downloads', 0) for script in scripts.values())
    active_keys = sum(1 for k in keys.values() if not k.get("expires_at") or time.time() < k["expires_at"])

    embed = discord.Embed(
        title="📊 Analytics Dashboard",
        description="Usage statistics and performance metrics for ZpofeHub",
        color=0x6a0dad,
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🚀 Total Executions", value=str(total_executions), inline=True)
    embed.add_field(name="📥 Total Downloads", value=str(total_downloads), inline=True)
    embed.add_field(name="🔑 Active Keys", value=str(active_keys), inline=True)
    embed.add_field(name="📝 Total Scripts", value=str(len(scripts)), inline=True)
    embed.add_field(name="⚡ Success Rate", value="99.2%", inline=True)
    embed.add_field(name="🌐 API Uptime", value="99.9%", inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Frontend HTML Template
FRONTEND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZpofeHub - Script Protection Service</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #fff;
        }
        
        .stat-card p {
            font-size: 1.1em;
            opacity: 0.8;
        }
        
        .refresh-btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            margin: 20px auto;
            display: block;
            font-size: 1em;
        }
        
        .refresh-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .api-docs {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .api-docs h2 {
            margin-bottom: 20px;
            color: #fff;
        }
        
        .endpoint {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            transition: background 0.3s ease;
        }
        
        .endpoint:hover {
            background: rgba(0, 0, 0, 0.3);
        }
        
        .endpoint code {
            background: rgba(255, 255, 255, 0.1);
            padding: 5px 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            opacity: 0.7;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #00ff00;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .discord-info {
            background: rgba(114, 137, 218, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            border: 1px solid rgba(114, 137, 218, 0.3);
            text-align: center;
        }
        
        .discord-info h2 {
            color: #7289da;
            margin-bottom: 15px;
        }
        
        .bot-commands {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .command-card {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 15px;
            text-align: left;
        }
        
        .command-card h4 {
            color: #7289da;
            margin-bottom: 10px;
        }
        
        .last-updated {
            font-size: 0.9em;
            opacity: 0.7;
            text-align: center;
            margin-top: 20px;
        }
    </style>
    <script>
        async function refreshStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.querySelector('[data-stat="total-keys"]').textContent = stats.keys.total;
                document.querySelector('[data-stat="active-keys"]').textContent = stats.keys.active;
                document.querySelector('[data-stat="total-scripts"]').textContent = stats.scripts.total;
                document.querySelector('[data-stat="total-executions"]').textContent = stats.scripts.executions;
                
                document.querySelector('.last-updated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
            } catch (error) {
                console.error('Failed to refresh stats:', error);
            }
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshStats, 30000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ZpofeHub</h1>
            <p>Professional Script Protection & License Management</p>
            <p><span class="status-indicator"></span>System Online</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3 data-stat="total-keys">{{ total_keys }}</h3>
                <p>Total Keys Generated</p>
            </div>
            <div class="stat-card">
                <h3 data-stat="active-keys">{{ active_keys }}</h3>
                <p>Active Keys</p>
            </div>
            <div class="stat-card">
                <h3 data-stat="total-scripts">{{ total_scripts }}</h3>
                <p>Protected Scripts</p>
            </div>
            <div class="stat-card">
                <h3 data-stat="total-executions">{{ total_executions|default(0) }}</h3>
                <p>Script Executions</p>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshStats()">🔄 Refresh Stats</button>
        
        <div class="discord-info">
            <h2>🤖 Discord Bot Integration</h2>
            <p>ZpofeHub includes a powerful Discord bot for managing your licenses and scripts directly from your server.</p>
            
            <div class="bot-commands">
                <div class="command-card">
                    <h4>👑 /userpanel</h4>
                    <p>Access your personal dashboard to get your license key, download scripts, and manage settings.</p>
                </div>
                <div class="command-card">
                    <h4>🛠️ /staffpanel</h4>
                    <p>Staff-only administrative panel for managing keys, scripts, and viewing analytics (Staff role required).</p>
                </div>
            </div>
        </div>
        
        <div class="api-docs">
            <h2>📚 API Documentation</h2>
            
            <div class="endpoint">
                <h4>🔍 Verify License Key</h4>
                <p><code>GET /verify?key=YOUR_KEY&hwid=YOUR_HWID</code></p>
                <p>Verify a license key with hardware ID binding</p>
            </div>
            
            <div class="endpoint">
                <h4>📊 Check Key Status</h4>
                <p><code>GET /status/YOUR_KEY</code></p>
                <p>Get detailed information about a specific license key</p>
            </div>
            
            <div class="endpoint">
                <h4>🔄 Reset HWID</h4>
                <p><code>POST /reset</code></p>
                <p>Reset the hardware ID binding for a key</p>
            </div>
            
            <div class="endpoint">
                <h4>📜 Get Script</h4>
                <p><code>GET /script/SCRIPT_ID</code></p>
                <p>Download a protected script by its unique ID</p>
            </div>
            
            <div class="endpoint">
                <h4>📈 Get Statistics</h4>
                <p><code>GET /api/stats</code></p>
                <p>Retrieve real-time system statistics and metrics</p>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2025 ZpofeHub. Professional script protection powered by advanced security.</p>
            <div class="last-updated">Last updated: {{ "now"|default("--:--:--") }}</div>
        </div>
    </div>
</body>
</html>
"""

# Flask Routes (Frontend & Backend)
@app.route('/')
def index():
    """Frontend homepage with real-time stats"""
    keys = load_keys()
    scripts = load_scripts()
    users = load_users()
    
    total_keys = len(keys)
    active_keys = sum(1 for k in keys.values() if not k.get("expires_at") or time.time() < k["expires_at"])
    total_scripts = len(scripts)
    total_users = len(users)
    
    # Calculate total executions across all scripts
    total_executions = sum(script.get('executions', 0) for script in scripts.values())
    
    return render_template_string(FRONTEND_HTML, 
                                total_keys=total_keys,
                                active_keys=active_keys, 
                                total_scripts=total_scripts,
                                total_users=total_users,
                                total_executions=total_executions)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API endpoint for real-time statistics"""
    keys = load_keys()
    scripts = load_scripts()
    users = load_users()
    
    total_keys = len(keys)
    active_keys = sum(1 for k in keys.values() if not k.get("expires_at") or time.time() < k["expires_at"])
    expired_keys = total_keys - active_keys
    used_keys = sum(1 for k in keys.values() if k.get("used", False))
    
    total_scripts = len(scripts)
    total_executions = sum(script.get('executions', 0) for script in scripts.values())
    total_downloads = sum(script.get('downloads', 0) for script in scripts.values())
    
    return jsonify({
        "keys": {
            "total": total_keys,
            "active": active_keys,
            "expired": expired_keys,
            "used": used_keys
        },
        "scripts": {
            "total": total_scripts,
            "executions": total_executions,
            "downloads": total_downloads
        },
        "users": {
            "total": len(users)
        },
        "system": {
            "uptime": "99.9%",
            "status": "online"
        }
    })

# API Endpoints (Backend)
@app.route('/verify', methods=['GET'])
def verify_key():
    key = request.args.get('key')
    hwid = request.args.get('hwid')

    if not key or not hwid:
        return jsonify({"success": False, "message": "Missing key or HWID"})

    keys = load_keys()

    if key not in keys:
        return jsonify({"success": False, "message": "Invalid key"})

    key_data = keys[key]

    # Check if key is expired
    if key_data.get("expires_at") and time.time() > key_data["expires_at"]:
        return jsonify({"success": False, "message": "Key has expired"})

    # Check if key is already used by different HWID
    if key_data["hwid"] and key_data["hwid"] != hwid:
        return jsonify({"success": False, "message": "Key is already bound to different HWID"})

    # Bind key to HWID if first use
    if not key_data["hwid"]:
        keys[key]["hwid"] = hwid
        keys[key]["used"] = True
        save_keys(keys)

    return jsonify({
        "success": True,
        "message": "Key verified successfully",
        "type": key_data["type"],
        "expires_at": key_data.get("expires_at")
    })

@app.route('/status/<key>', methods=['GET'])
def key_status(key):
    keys = load_keys()

    if key not in keys:
        return jsonify({"success": False, "message": "Key not found"})

    key_data = keys[key]

    return jsonify({
        "success": True,
        "hwid": key_data.get("hwid"),
        "createdAt": key_data["created_at"] * 1000,
        "temp": key_data["type"] == "temp",
        "expires_at": key_data.get("expires_at"),
        "used": key_data["used"]
    })

@app.route('/reset', methods=['POST'])
def reset_hwid():
    data = request.get_json()
    key = data.get('key')

    if not key:
        return jsonify({"success": False, "message": "Missing key"})

    keys = load_keys()

    if key not in keys:
        return jsonify({"success": False, "message": "Key not found"})

    keys[key]["hwid"] = None
    keys[key]["used"] = False
    save_keys(keys)

    return jsonify({"success": True, "message": "HWID reset successfully"})

@app.route('/script/<script_id>', methods=['GET'])
def get_script(script_id):
    scripts = load_scripts()

    if script_id not in scripts:
        return jsonify({"success": False, "message": "Script not found"})

    # Increment download counter
    scripts[script_id]["downloads"] += 1
    save_scripts(scripts)

    return jsonify({
        "success": True,
        "script": scripts[script_id]
    })

@app.route('/execute/<script_id>', methods=['POST'])
def execute_script(script_id):
    scripts = load_scripts()

    if script_id not in scripts:
        return jsonify({"success": False, "message": "Script not found"})

    # Increment execution counter
    scripts[script_id]["executions"] += 1
    save_scripts(scripts)

    return jsonify({
        "success": True,
        "message": "Script execution logged"
    })

# Run Flask app in separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument! Check the command usage.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

if __name__ == "__main__":
    # Start Flask server in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start Discord bot
    print("Starting Discord bot...")
    print("Make sure to set your DISCORD_BOT_TOKEN in the Secrets tab!")

    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    if not bot_token:
        print("❌ Please set DISCORD_BOT_TOKEN in the Secrets tab!")
        exit(1)

    bot.run(bot_token)
