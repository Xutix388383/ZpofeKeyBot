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
import threading
from flask import Flask, render_template_string, request, redirect, session, flash, jsonify

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Key storage file
KEYS_FILE = "keys.json"
USERS_FILE = "users.json"
HWID_COOLDOWNS_FILE = "hwid_cooldowns.json"
BLACKLIST_FILE = "blacklist.json"

# Required role IDs
BUYER_ROLE_ID = 1406653314589786204
STAFF_ROLE_ID = 1399949855799119952

# Flask admin authentication key
ADMIN_KEY = "ZpofeAdmin97492"

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

# Script functions removed - using API instead

def load_hwid_cooldowns():
    if os.path.exists(HWID_COOLDOWNS_FILE):
        with open(HWID_COOLDOWNS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_hwid_cooldowns(cooldowns):
    with open(HWID_COOLDOWNS_FILE, 'w') as f:
        json.dump(cooldowns, f, indent=2)

def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(blacklist, f, indent=2)

# Generate random key
def generate_key():
    return "ZPOFES-" + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))

# Script ID generator removed - using API instead

# Bot events
@bot.event
async def on_ready():
    print(f'✅ {bot.user} has connected to Discord!')
    print(f'📊 Bot ID: {bot.user.id}')
    print(f'🌐 Connected to {len(bot.guilds)} guild(s)')

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")

        # Create data files if they don't exist
        for file_path in [KEYS_FILE, USERS_FILE, HWID_COOLDOWNS_FILE, BLACKLIST_FILE]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
                print(f"📁 Created {file_path}")

        print("🚀 ZpofeHub Bot is ready and operational!")

    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
        print("Bot will continue running but slash commands may not work")

# User Panel Command
@bot.tree.command(name="userpanel", description="Access your ZpofeHub user panel")
async def user_panel(interaction: discord.Interaction):
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
class UserPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Get My Key", style=discord.ButtonStyle.success, emoji="🔑")
    async def get_my_key(self, interaction: discord.Interaction, button: discord.ui.Button):
        blacklist = load_blacklist()
        if str(interaction.user.id) in blacklist:
            embed = discord.Embed(
                title="⛔ Access Denied",
                description="Your account has been blacklisted from accessing ZpofeHub services.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

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

    @discord.ui.button(label="Get Script", style=discord.ButtonStyle.primary, emoji="📜")
    async def get_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        blacklist = load_blacklist()
        if str(interaction.user.id) in blacklist:
            embed = discord.Embed(
                title="⛔ Access Denied",
                description="Your account has been blacklisted from accessing ZpofeHub services.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

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

    @discord.ui.button(label="Settings", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        blacklist = load_blacklist()
        if str(interaction.user.id) in blacklist:
            embed = discord.Embed(
                title="⛔ Access Denied",
                description="Your account has been blacklisted from accessing ZpofeHub services.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

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

class UserSettingsView(discord.ui.View):
    def __init__(self, on_cooldown=False):
        super().__init__(timeout=300)
        self.on_cooldown = on_cooldown

    @discord.ui.button(label="Reset HWID", style=discord.ButtonStyle.danger, emoji="🔄")
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

    @discord.ui.button(label="Account Info", style=discord.ButtonStyle.secondary, emoji="📊")
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

# Function implementations
async def reset_user_hwid(interaction):
    user_id = str(interaction.user.id)
    cooldowns = load_hwid_cooldowns()

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

    keys[user_key]["hwid"] = None
    keys[user_key]["used"] = False
    save_keys(keys)

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

async def show_user_key(interaction):
    user_id = str(interaction.user.id)
    keys = load_keys()

    user_key = None
    for key, data in keys.items():
        if data.get("owner") == user_id:
            user_key = key
            break

    if not user_key:
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
    try:
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

        await interaction.user.send(embed=embed)

        confirm_embed = discord.Embed(
            title="✅ Script Sent",
            description="Your script loadstring has been sent to your DMs!",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ DM Failed",
            description="Unable to send DM. Please enable DMs from server members and try again.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def show_user_settings(interaction):
    cooldowns = load_hwid_cooldowns()
    user_id = str(interaction.user.id)

    cooldown_remaining = 0
    if user_id in cooldowns:
        last_reset = cooldowns[user_id]
        cooldown_remaining = max(0, 86400 - (time.time() - last_reset))

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

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument! Check the command usage.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

# Flask web server setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Authentication decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session or not session['authenticated']:
            return redirect('/login')
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ZpofeHub Admin Login</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d); 
            color: white; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
        }
        .login-container { 
            background: rgba(0,0,0,0.8); 
            padding: 40px; 
            border-radius: 15px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.5); 
            text-align: center; 
            min-width: 400px; 
        }
        h1 { color: #6a0dad; margin-bottom: 30px; }
        input { 
            width: 100%; 
            padding: 15px; 
            margin: 10px 0; 
            border: none; 
            border-radius: 8px; 
            background: #333; 
            color: white; 
            font-size: 16px; 
        }
        button { 
            width: 100%; 
            padding: 15px; 
            background: #6a0dad; 
            border: none; 
            border-radius: 8px; 
            color: white; 
            font-size: 16px; 
            cursor: pointer; 
            margin-top: 20px; 
        }
        button:hover { background: #8a2be2; }
        .error { color: #ff4444; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🚀 ZpofeHub Admin Panel</h1>
        <form method="POST">
            <input type="password" name="admin_key" placeholder="Enter Admin Key" required>
            <button type="submit">🔐 Login</button>
        </form>
        {% if error %}
        <div class="error">❌ {{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ZpofeHub Admin Dashboard</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d); 
            color: white; 
            margin: 0; 
            padding: 20px; 
        }
        .header { 
            background: rgba(0,0,0,0.8); 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 20px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }
        .nav { 
            display: flex; 
            gap: 20px; 
        }
        .nav a { 
            color: #6a0dad; 
            text-decoration: none; 
            padding: 10px 20px; 
            background: rgba(106, 13, 173, 0.2); 
            border-radius: 5px; 
            transition: all 0.3s; 
        }
        .nav a:hover { background: rgba(106, 13, 173, 0.5); }
        .nav a.active { background: #6a0dad; color: white; }
        .container { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }
        .card { 
            background: rgba(0,0,0,0.8); 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 4px solid #6a0dad; 
        }
        .stat { 
            font-size: 2em; 
            color: #6a0dad; 
            font-weight: bold; 
        }
        .logout { 
            background: #ff4444; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
        }
        .success { color: #44ff44; }
        .error { color: #ff4444; }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background: rgba(0,0,0,0.5); 
            border-radius: 8px; 
            overflow: hidden; 
        }
        th, td { 
            padding: 15px; 
            text-align: left; 
            border-bottom: 1px solid #333; 
        }
        th { background: #6a0dad; }
        .btn { 
            padding: 8px 15px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            margin: 2px; 
        }
        .btn-primary { background: #6a0dad; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; color: #6a0dad; }
        .form-group input, .form-group textarea { 
            width: 100%; 
            padding: 10px; 
            border: none; 
            border-radius: 5px; 
            background: #333; 
            color: white; 
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 ZpofeHub Admin Panel</h1>
        <div class="nav">
            <a href="/admin" class="{% if page == 'dashboard' %}active{% endif %}">📊 Dashboard</a>
            <a href="/admin/keys" class="{% if page == 'keys' %}active{% endif %}">🔑 Keys</a>
            <a href="/admin/api" class="{% if page == 'api' %}active{% endif %}">🔗 API</a>
            <a href="/admin/users" class="{% if page == 'users' %}active{% endif %}">👥 Users</a>
            <a href="/admin/blacklist" class="{% if page == 'blacklist' %}active{% endif %}">⛔ Blacklist</a>
            <button class="logout" onclick="window.location.href='/logout'">🚪 Logout</button>
        </div>
    </div>

    {% if messages %}
        {% for message in messages %}
            <div class="card {{ message.1 }}">{{ message.0 }}</div>
        {% endfor %}
    {% endif %}

    {{ content|safe }}
</body>
</html>
'''

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ZpofeHub</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #1a1a1a, #2d2d2d); color: white; text-align: center; padding: 50px; margin: 0; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { color: #00ff00; }
            .admin-link { 
                display: inline-block; 
                margin-top: 30px; 
                padding: 15px 30px; 
                background: #6a0dad; 
                color: white; 
                text-decoration: none; 
                border-radius: 8px; 
                transition: background 0.3s; 
            }
            .admin-link:hover { background: #8a2be2; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ZpofeHub</h1>
            <h2>Premium Script Protection & License Management</h2>
            <p class="status">✅ Bot Status: Online and Operational</p>
            <p>Join our Discord server to access premium scripts and license management.</p>
            <a href="/login" class="admin-link">🔐 Admin Panel</a>
        </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin_key = request.form.get('admin_key')
        if admin_key == ADMIN_KEY:
            session['authenticated'] = True
            return redirect('/admin')
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid admin key")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/admin')
@login_required
def admin_dashboard():
    keys = load_keys()
    blacklist = load_blacklist()

    total_keys = len(keys)
    active_keys = sum(1 for k in keys.values() if not k.get("expires_at") or time.time() < k["expires_at"])
    blacklisted_users = len(blacklist)

    content = f'''
    <div class="container">
        <div class="card">
            <h3>📊 System Statistics</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
                <div style="text-align: center;">
                    <div class="stat">{total_keys}</div>
                    <div>Total Keys</div>
                </div>
                <div style="text-align: center;">
                    <div class="stat">{active_keys}</div>
                    <div>Active Keys</div>
                </div>
                <div style="text-align: center;">
                    <div class="stat">API</div>
                    <div>Mode</div>
                </div>
                <div style="text-align: center;">
                    <div class="stat">{blacklisted_users}</div>
                    <div>Blacklisted Users</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>🚀 Quick Actions</h3>
            <a href="/admin/keys/generate" class="btn btn-success">🆕 Generate New Key</a>
            <a href="/admin/scripts/upload" class="btn btn-primary">📤 Upload Script</a>
            <a href="/admin/users/blacklist" class="btn btn-danger">⛔ Blacklist User</a>
        </div>
    </div>
    '''

    return render_template_string(DASHBOARD_TEMPLATE, content=content, page='dashboard')

@app.route('/admin/keys')
@login_required
def admin_keys():
    keys = load_keys()

    content = '''
    <div class="card">
        <h3>🔑 License Key Management</h3>
        <a href="/admin/keys/generate" class="btn btn-success">🆕 Generate New Key</a>
        <table style="margin-top: 20px;">
            <tr>
                <th>Key</th>
                <th>Type</th>
                <th>Status</th>
                <th>Owner</th>
                <th>Created</th>
                <th>Actions</th>
            </tr>
    '''

    for key, data in keys.items():
        status = "🔴 Expired" if data.get("expires_at") and time.time() > data["expires_at"] else "🟢 Active"
        used = "✅ Used" if data["used"] else "❌ Unused"
        owner = data.get('owner', 'Unassigned')
        created = datetime.fromtimestamp(data['created_at']).strftime('%Y-%m-%d %H:%M')

        content += f'''
            <tr>
                <td><code>{key[:20]}...</code></td>
                <td>{data['type']}</td>
                <td>{status} • {used}</td>
                <td>{owner}</td>
                <td>{created}</td>
                <td>
                    <a href="/admin/keys/delete/{key}" class="btn btn-danger" onclick="return confirm('Delete this key?')">🗑️ Delete</a>
                </td>
            </tr>
        '''

    content += '''
        </table>
    </div>
    '''

    return render_template_string(DASHBOARD_TEMPLATE, content=content, page='keys')

@app.route('/admin/keys/generate', methods=['GET', 'POST'])
@login_required
def generate_admin_key():
    if request.method == 'POST':
        key_type = request.form.get('key_type', 'perm')
        key = generate_key()
        keys = load_keys()

        keys[key] = {
            "type": key_type,
            "created_by": "admin",
            "created_at": time.time(),
            "expires_at": None,
            "hwid": None,
            "used": False,
            "owner": None
        }

        save_keys(keys)

        content = f'''
        <div class="card success">
            <h3>✅ Key Generated Successfully</h3>
            <p><strong>New Key:</strong> <code>{key}</code></p>
            <p><strong>Type:</strong> {key_type}</p>
            <a href="/admin/keys" class="btn btn-primary">← Back to Keys</a>
        </div>
        '''
        return render_template_string(DASHBOARD_TEMPLATE, content=content, page='keys')

    content = '''
    <div class="card">
        <h3>🆕 Generate New Key</h3>
        <form method="POST">
            <div class="form-group">
                <label>Key Type:</label>
                <select name="key_type" style="width: 100%; padding: 10px; border: none; border-radius: 5px; background: #333; color: white;">
                    <option value="perm">Permanent</option>
                    <option value="temp">Temporary</option>
                </select>
            </div>
            <button type="submit" class="btn btn-success">🔑 Generate Key</button>
            <a href="/admin/keys" class="btn btn-primary">← Back</a>
        </form>
    </div>
    '''

    return render_template_string(DASHBOARD_TEMPLATE, content=content, page='keys')

@app.route('/admin/keys/delete/<key>')
@login_required
def delete_key(key):
    keys = load_keys()
    if key in keys:
        del keys[key]
        save_keys(keys)
    return redirect('/admin/keys')

@app.route('/admin/scripts')
@login_required
def admin_scripts():
    scripts = load_scripts()

    content = '''
    <div class="card">
        <h3>📜 Script Management</h3>
        <a href="/admin/scripts/upload" class="btn btn-success">📤 Upload Script</a>
        <table style="margin-top: 20px;">
            <tr>
                <th>Name</th>
                <th>ID</th>
                <th>Description</th>
                <th>Downloads</th>
                <th>Executions</th>
                <th>Created</th>
            </tr>
    '''

    for script_id, data in scripts.items():
        created = datetime.fromtimestamp(data['created_at']).strftime('%Y-%m-%d %H:%M')

        content += f'''
            <tr>
                <td><strong>{data['name']}</strong></td>
                <td><code>{script_id}</code></td>
                <td>{data['description'][:50]}...</td>
                <td>{data['downloads']}</td>
                <td>{data['executions']}</td>
                <td>{created}</td>
            </tr>
        '''

    content += '''
        </table>
    </div>
    '''

    return render_template_string(DASHBOARD_TEMPLATE, content=content, page='scripts')

@app.route('/admin/scripts/upload', methods=['GET', 'POST'])
@login_required
def upload_script():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', 'No description provided')

        scripts = load_scripts()
        script_id = generate_script_id()

        scripts[script_id] = {
            "name": name,
            "description": description,
            "owner": "admin",
            "created_at": time.time(),
            "downloads": 0,
            "executions": 0
        }

        save_scripts(scripts)

        content = f'''
        <div class="card success">
            <h3>✅ Script Uploaded Successfully</h3>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Script ID:</strong> <code>{script_id}</code></p>
            <a href="/admin/scripts" class="btn btn-primary">← Back to Scripts</a>
        </div>
        '''
        return render_template_string(DASHBOARD_TEMPLATE, content=content, page='scripts')

    content = '''
    <div class="card">
        <h3>📤 Upload New Script</h3>
        <form method="POST">
            <div class="form-group">
                <label>Script Name:</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Description:</label>
                <textarea name="description" rows="3"></textarea>
            </div>
            <button type="submit" class="btn btn-success">📤 Upload Script</button>
            <a href="/admin/scripts" class="btn btn-primary">← Back</a>
        </form>
    </div>
    '''

    return render_template_string(DASHBOARD_TEMPLATE, content=content, page='scripts')

@app.route('/admin/users')
@login_required
def admin_users():
    keys = load_keys()
    cooldowns = load_hwid_cooldowns()

    content = '''
    <div class="card">
        <h3>👥 User Management</h3>
        <a href="/admin/users/reset-hwid" class="btn btn-primary">🔄 Reset User HWID</a>
        <a href="/admin/users/blacklist" class="btn btn-danger">⛔ Blacklist User</a>
        <table style="margin-top: 20px;">
            <tr>
                <th>User ID</th>
                <th>Key</th>
                <th>HWID Status</th>
                <th>Last HWID Reset</th>
                <th>Actions</th>
            </tr>
    '''

    user_keys = {}
    for key, data in keys.items():
        if data.get('owner'):
            user_keys[data['owner']] = key

    for user_id, key in user_keys.items():
        key_data = keys[key]
        hwid_status = "Bound" if key_data['hwid'] else "Not bound"
        last_reset = "Never"
        if user_id in cooldowns:
            last_reset = datetime.fromtimestamp(cooldowns[user_id]).strftime('%Y-%m-%d %H:%M')

        content += f'''
            <tr>
                <td>{user_id}</td>
                <td><code>{key[:20]}...</code></td>
                <td>{hwid_status}</td>
                <td>{last_reset}</td>
                <td>
                    <a href="/admin/users/reset-hwid/{user_id}" class="btn btn-primary">🔄 Reset HWID</a>
                    <a href="/admin/users/blacklist/{user_id}" class="btn btn-danger">⛔ Blacklist</a>
                </td>
            </tr>
        '''

    content += '''
        </table>
    </div>
    '''

    return render_template_string(DASHBOARD_TEMPLATE, content=content, page='users')

@app.route('/admin/users/reset-hwid/<user_id>')
@login_required
def reset_user_hwid_admin(user_id):
    keys = load_keys()
    user_key = None

    for key, data in keys.items():
        if data.get("owner") == user_id:
            user_key = key
            break

    if user_key:
        keys[user_key]["hwid"] = None
        keys[user_key]["used"] = False
        save_keys(keys)

    return redirect('/admin/users')

@app.route('/admin/blacklist')
@login_required
def admin_blacklist():
    blacklist = load_blacklist()

    content = '''
    <div class="card">
        <h3>⛔ Blacklist Management</h3>
        <a href="/admin/users/blacklist" class="btn btn-danger">⛔ Blacklist User</a>
        <table style="margin-top: 20px;">
            <tr>
                <th>User ID</th>
                <th>Reason</th>
                <th>Blacklisted Date</th>
                <th>Actions</th>
            </tr>
    '''

    for user_id, data in blacklist.items():
        blacklisted_at = datetime.fromtimestamp(data.get('blacklisted_at', time.time())).strftime('%Y-%m-%d %H:%M')
        reason = data.get('reason', 'No reason provided')

        content += f'''
            <tr>
                <td>{user_id}</td>
                <td>{reason}</td>
                <td>{blacklisted_at}</td>
                <td>
                    <a href="/admin/blacklist/remove/{user_id}" class="btn btn-success">✅ Remove</a>
                </td>
            </tr>
        '''

    content += '''
        </table>
    </div>
    '''

    return render_template_string(DASHBOARD_TEMPLATE, content=content, page='blacklist')

@app.route('/admin/users/blacklist', methods=['GET', 'POST'])
@login_required
def blacklist_user():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        reason = request.form.get('reason', 'No reason provided')

        blacklist = load_blacklist()
        blacklist[user_id] = {
            "reason": reason,
            "blacklisted_at": time.time(),
            "blacklisted_by": "admin"
        }
        save_blacklist(blacklist)

        return redirect('/admin/blacklist')

    content = '''
    <div class="card">
        <h3>⛔ Blacklist User</h3>
        <form method="POST">
            <div class="form-group">
                <label>User ID:</label>
                <input type="text" name="user_id" required>
            </div>
            <div class="form-group">
                <label>Reason:</label>
                <textarea name="reason" rows="3"></textarea>
            </div>
            <button type="submit" class="btn btn-danger">⛔ Blacklist User</button>
            <a href="/admin/blacklist" class="btn btn-primary">← Back</a>
        </form>
    </div>
    '''

    return render_template_string(DASHBOARD_TEMPLATE, content=content, page='blacklist')

@app.route('/admin/blacklist/remove/<user_id>')
@login_required
def remove_blacklist(user_id):
    blacklist = load_blacklist()
    if user_id in blacklist:
        del blacklist[user_id]
        save_blacklist(blacklist)
    return redirect('/admin/blacklist')

@app.route('/health')
def health():
    return {"status": "ok", "bot_status": "running"}

@app.route('/api/status')
def api_status():
    return {
        "status": "healthy",
        "service": "ZpofeHub Discord Bot",
        "uptime": "online",
        "bot_ready": bot.is_ready() if 'bot' in globals() else False
    }

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    print("🚀 Starting ZpofeHub Discord Bot...")
    print("🌐 Starting Flask admin server on port 5000...")

    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    print("Checking for bot token...")

    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    if not bot_token:
        print("❌ DISCORD_BOT_TOKEN not found!")
        print("Please set your bot token in environment variables")
        exit(1)

    print("✅ Bot token found, starting bot...")
    print(f"🔐 Admin panel accessible at: http://localhost:5000/login")
    print(f"🔑 Admin key: {ADMIN_KEY}")

    try:
        bot.run(bot_token)
    except discord.LoginFailure:
        print("❌ Invalid bot token! Please check your DISCORD_BOT_TOKEN")
        exit(1)
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
        exit(1)