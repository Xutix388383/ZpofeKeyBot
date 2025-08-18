
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Role IDs from environment variables with fallbacks
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID', '1399949855799119952'))
BUYER_ROLE_ID = int(os.getenv('BUYER_ROLE_ID', '1406653314589786204'))

# Data files
SCRIPTS_FILE = 'scripts.json'
ORDERS_FILE = 'orders.json'
TICKETS_FILE = 'tickets.json'
USER_SCRIPTS_FILE = 'user_scripts.json'

def init_data_files():
    """Initialize data files if they don't exist"""
    files = [SCRIPTS_FILE, ORDERS_FILE, TICKETS_FILE, USER_SCRIPTS_FILE]
    defaults = [[], [], [], {}]
    
    for file_path, default in zip(files, defaults):
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(default, f)

def load_data(file_path):
    """Load data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return [] if file_path != USER_SCRIPTS_FILE else {}

def save_data(file_path, data):
    """Save data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_scripts():
    return load_data(SCRIPTS_FILE)

def save_scripts(scripts):
    save_data(SCRIPTS_FILE, scripts)

def load_orders():
    return load_data(ORDERS_FILE)

def save_orders(orders):
    save_data(ORDERS_FILE, orders)

def load_tickets():
    return load_data(TICKETS_FILE)

def save_tickets(tickets):
    save_data(TICKETS_FILE, tickets)

def load_user_scripts():
    return load_data(USER_SCRIPTS_FILE)

def save_user_scripts(user_scripts):
    save_data(USER_SCRIPTS_FILE, user_scripts)

def is_admin(user):
    """Check if user has admin role"""
    return any(role.id == ADMIN_ROLE_ID for role in user.roles)

def has_buyer_role(user):
    """Check if user has buyer role"""
    return any(role.id == BUYER_ROLE_ID for role in user.roles)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    init_data_files()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name='shop', description='Open the script marketplace shop (Admin only)')
async def shop(interaction: discord.Interaction):
    """Display the shop panel with cart system - admin only"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You need administrator permissions to access the shop!", ephemeral=True)
        return
    
    scripts = load_scripts()
    
    if not scripts:
        embed = discord.Embed(
            title="🛒 Script Shop",
            description="No scripts available at the moment.\nContact an admin to add some scripts!",
            color=0x667eea
        )
        await interaction.response.send_message(embed=embed)
        return
    
    # Create public shop embed (shows available scripts)
    embed = discord.Embed(
        title="🛒 Zpofe's Script Shop",
        description="Premium scripts for your projects. Click 'Browse Shop' to start shopping!",
        color=0x667eea,
        timestamp=datetime.now()
    )
    
    # Show available scripts in a preview format
    script_preview = ""
    for i, script in enumerate(scripts[:6]):  # Show first 6 scripts as preview
        script_preview += f"**{script['name']}** - ${script['price']:.2f} ({script['category']})\n"
    
    if len(scripts) > 6:
        script_preview += f"\n*...and {len(scripts) - 6} more scripts available!*"
    
    embed.add_field(
        name="📚 Available Scripts",
        value=script_preview,
        inline=False
    )
    
    embed.add_field(
        name="🛍️ How to Shop",
        value="Click the 'Browse Shop' button below to open your personal shopping interface!",
        inline=False
    )
    
    embed.set_footer(text="🛍️ Public Shop Display | Personal shopping available", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    
    # Create public shop view
    view = PublicShopView(scripts)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name='edit', description='Complete marketplace editor and setup (Admin only)')
async def edit_marketplace(interaction: discord.Interaction):
    """Complete marketplace editor - admin only"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You need administrator permissions to access the marketplace editor!", ephemeral=True)
        return
    
    scripts = load_scripts()
    orders = load_orders()
    tickets = load_tickets()
    user_scripts = load_user_scripts()
    
    # Calculate statistics
    total_revenue = sum(order.get('total_price', 0) for order in orders)
    pending_orders = len([o for o in orders if o.get('status') == 'pending'])
    verified_tickets = len([t for t in tickets if t.get('status') == 'verified'])
    total_users_with_scripts = len(user_scripts)
    
    embed = discord.Embed(
        title="⚙️ Marketplace Editor & Setup",
        description="Complete marketplace configuration and management system",
        color=0x9932cc,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="📊 Current Statistics",
        value=f"**Scripts:** {len(scripts)}\n**Orders:** {len(orders)}\n**Revenue:** ${total_revenue:.2f}\n**Active Users:** {total_users_with_scripts}",
        inline=True
    )
    
    embed.add_field(
        name="🎫 Ticket Status",
        value=f"**Total:** {len(tickets)}\n**Verified:** {verified_tickets}\n**Pending:** {len(tickets) - verified_tickets}",
        inline=True
    )
    
    embed.add_field(
        name="🛠️ Quick Setup",
        value="Use the buttons below for:\n• Initial marketplace setup\n• Script management\n• User management\n• Advanced configuration",
        inline=False
    )
    
    embed.set_footer(text="Marketplace Editor | Complete Control Panel")
    
    view = MarketplaceEditorView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name='admin', description='Access admin panel (Admin only)')
async def admin_panel(interaction: discord.Interaction):
    """Complete admin panel - admin only"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You need administrator permissions to access the admin panel!", ephemeral=True)
        return
    
    scripts = load_scripts()
    orders = load_orders()
    tickets = load_tickets()
    user_scripts = load_user_scripts()
    
    # Calculate statistics
    total_revenue = sum(order.get('price', 0) for order in orders)
    pending_orders = len([o for o in orders if o.get('status') == 'pending'])
    verified_tickets = len([t for t in tickets if t.get('status') == 'verified'])
    total_users_with_scripts = len(user_scripts)
    
    embed = discord.Embed(
        title="🔧 Admin Control Panel",
        description="Complete marketplace management system",
        color=0xffa500,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="📊 Statistics",
        value=f"**Scripts:** {len(scripts)}\n**Orders:** {len(orders)}\n**Revenue:** ${total_revenue:.2f}\n**Pending Orders:** {pending_orders}",
        inline=True
    )
    
    embed.add_field(
        name="🎫 Tickets",
        value=f"**Total:** {len(tickets)}\n**Verified:** {verified_tickets}\n**Pending:** {len(tickets) - verified_tickets}",
        inline=True
    )
    
    embed.add_field(
        name="👥 Users",
        value=f"**With Scripts:** {total_users_with_scripts}\n**Total Assignments:** {sum(len(scripts) for scripts in user_scripts.values())}",
        inline=True
    )
    
    embed.add_field(
        name="🛠️ Management Tools",
        value="Use the buttons below to manage scripts, users, orders, and tickets",
        inline=False
    )
    
    embed.set_footer(text="Admin Panel | Full Marketplace Control")
    
    view = AdminPanelView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class AdminPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
    
    @discord.ui.button(label="📝 Manage Scripts", style=discord.ButtonStyle.primary, emoji="📚")
    async def manage_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        scripts = load_scripts()
        
        embed = discord.Embed(
            title="📚 Script Management",
            description="Manage all marketplace scripts",
            color=0x667eea
        )
        
        if scripts:
            script_list = ""
            for script in scripts[:10]:  # Show first 10
                script_list += f"**ID {script['id']}:** {script['name']} - ${script['price']:.2f}\n"
            
            embed.add_field(
                name="📋 Current Scripts",
                value=script_list or "No scripts available",
                inline=False
            )
            
            if len(scripts) > 10:
                embed.add_field(
                    name="📊 Total",
                    value=f"Showing 10 of {len(scripts)} scripts",
                    inline=False
                )
        else:
            embed.add_field(
                name="📋 Current Scripts",
                value="No scripts added yet",
                inline=False
            )
        
        view = ScriptManagementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="👥 Manage Users", style=discord.ButtonStyle.secondary, emoji="👤")
    async def manage_users(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_scripts = load_user_scripts()
        
        embed = discord.Embed(
            title="👥 User Management",
            description="Assign scripts to users and manage access",
            color=0x9f7aea
        )
        
        if user_scripts:
            user_list = ""
            for user_id, script_ids in list(user_scripts.items())[:8]:
                user_list += f"<@{user_id}>: {len(script_ids)} scripts\n"
            
            embed.add_field(
                name="👤 Users with Scripts",
                value=user_list or "No users with scripts",
                inline=False
            )
        else:
            embed.add_field(
                name="👤 Users with Scripts",
                value="No users have scripts assigned",
                inline=False
            )
        
        view = UserManagementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🎫 Manage Tickets", style=discord.ButtonStyle.success, emoji="🎟️")
    async def manage_tickets(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_tickets()
        
        embed = discord.Embed(
            title="🎫 Ticket Management",
            description="Verify payments and manage customer tickets",
            color=0x28a745
        )
        
        if tickets:
            recent_tickets = sorted(tickets, key=lambda x: x['created_at'], reverse=True)[:5]
            ticket_list = ""
            
            for ticket in recent_tickets:
                status_emoji = "✅" if ticket['status'] == 'verified' else "⏳"
                ticket_list += f"{status_emoji} **#{ticket['id']}** - <@{ticket['user_id']}> ({ticket['status']})\n"
            
            embed.add_field(
                name="🎟️ Recent Tickets",
                value=ticket_list,
                inline=False
            )
            
            pending_count = len([t for t in tickets if t['status'] == 'pending'])
            embed.add_field(
                name="📊 Summary",
                value=f"**Total:** {len(tickets)}\n**Pending:** {pending_count}\n**Verified:** {len(tickets) - pending_count}",
                inline=False
            )
        else:
            embed.add_field(
                name="🎟️ Tickets",
                value="No tickets found",
                inline=False
            )
        
        view = TicketManagementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📊 View Orders", style=discord.ButtonStyle.secondary, emoji="📋")
    async def view_orders(self, interaction: discord.Interaction, button: discord.ui.Button):
        orders = load_orders()
        
        embed = discord.Embed(
            title="📋 Order Management",
            description="View and manage customer orders",
            color=0x6c757d
        )
        
        if orders:
            recent_orders = sorted(orders, key=lambda x: x['created_at'], reverse=True)[:5]
            order_list = ""
            
            for order in recent_orders:
                order_list += f"**#{order['id']}** - {order.get('buyer_discord', 'Unknown')} - ${order.get('total_price', 0):.2f}\n"
            
            embed.add_field(
                name="🛒 Recent Orders",
                value=order_list,
                inline=False
            )
            
            total_revenue = sum(order.get('total_price', 0) for order in orders)
            embed.add_field(
                name="💰 Statistics",
                value=f"**Total Orders:** {len(orders)}\n**Total Revenue:** ${total_revenue:.2f}",
                inline=False
            )
        else:
            embed.add_field(
                name="🛒 Orders",
                value="No orders found",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ScriptManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="➕ Add Script", style=discord.ButtonStyle.success, emoji="📝")
    async def add_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddScriptModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="✏️ Edit Script", style=discord.ButtonStyle.primary, emoji="📝")
    async def edit_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EditScriptModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Delete Script", style=discord.ButtonStyle.danger, emoji="❌")
    async def delete_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DeleteScriptModal()
        await interaction.response.send_modal(modal)

class UserManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="➕ Assign Script", style=discord.ButtonStyle.success, emoji="📋")
    async def assign_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AssignScriptModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="👤 View User Scripts", style=discord.ButtonStyle.primary, emoji="👥")
    async def view_user_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ViewUserScriptsModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Remove Scripts", style=discord.ButtonStyle.danger, emoji="❌")
    async def remove_user_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RemoveUserScriptsModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏷️ Give Buyer Role", style=discord.ButtonStyle.secondary, emoji="🎫")
    async def give_buyer_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GiveBuyerRoleModal()
        await interaction.response.send_modal(modal)

class TicketManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="✅ Verify Payment", style=discord.ButtonStyle.success, emoji="💳")
    async def verify_payment(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = VerifyPaymentModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 View All Tickets", style=discord.ButtonStyle.primary, emoji="🎫")
    async def view_all_tickets(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_tickets()
        
        embed = discord.Embed(
            title="🎫 All Tickets",
            description=f"Complete list of payment tickets",
            color=0x667eea
        )
        
        if tickets:
            for ticket in tickets[-10:]:  # Show last 10 tickets
                status_emoji = "✅" if ticket['status'] == 'verified' else "⏳"
                embed.add_field(
                    name=f"{status_emoji} Ticket #{ticket['id']}",
                    value=f"**User:** <@{ticket['user_id']}>\n**Order:** #{ticket['order_id']}\n**Status:** {ticket['status'].title()}\n**Date:** {ticket['created_at'][:10]}",
                    inline=True
                )
            
            if len(tickets) > 10:
                embed.set_footer(text=f"Showing 10 most recent of {len(tickets)} total tickets")
        else:
            embed.add_field(
                name="No Tickets",
                value="No payment tickets found",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Modal classes for admin functions
class AddScriptModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Add New Script")
        
        self.name = discord.ui.TextInput(
            label="Script Name",
            placeholder="Enter script name",
            required=True,
            max_length=100
        )
        
        self.price = discord.ui.TextInput(
            label="Price ($)",
            placeholder="9.99",
            required=True,
            max_length=10
        )
        
        self.category = discord.ui.TextInput(
            label="Category",
            placeholder="e.g., Discord Bot, Automation, Gaming",
            required=True,
            max_length=50
        )
        
        self.description = discord.ui.TextInput(
            label="Description",
            placeholder="Describe what this script does...",
            required=True,
            style=discord.TextStyle.long,
            max_length=1000
        )
        
        self.add_item(self.name)
        self.add_item(self.price)
        self.add_item(self.category)
        self.add_item(self.description)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            price = float(self.price.value)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Price",
                description="Please enter a valid price (e.g., 9.99)",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        scripts = load_scripts()
        
        script = {
            'id': len(scripts) + 1,
            'name': self.name.value,
            'description': self.description.value,
            'price': price,
            'category': self.category.value,
            'created_at': datetime.now().isoformat()
        }
        
        scripts.append(script)
        save_scripts(scripts)
        
        embed = discord.Embed(
            title="✅ Script Added Successfully!",
            description=f"**{self.name.value}** has been added to the shop!",
            color=0x28a745
        )
        
        embed.add_field(
            name="📄 Script Details",
            value=f"**ID:** {script['id']}\n**Price:** ${price:.2f}\n**Category:** {self.category.value}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AssignScriptModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Assign Script to User")
        
        self.user_id = discord.ui.TextInput(
            label="User ID",
            placeholder="Enter Discord user ID",
            required=True,
            max_length=20
        )
        
        self.script_id = discord.ui.TextInput(
            label="Script ID",
            placeholder="Enter script ID to assign",
            required=True,
            max_length=10
        )
        
        self.add_item(self.user_id)
        self.add_item(self.script_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            script_id = int(self.script_id.value)
            user_id = self.user_id.value
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description="Please enter valid user ID and script ID",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        scripts = load_scripts()
        script = next((s for s in scripts if s['id'] == script_id), None)
        
        if not script:
            embed = discord.Embed(
                title="❌ Script Not Found",
                description=f"No script found with ID {script_id}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_scripts = load_user_scripts()
        
        if user_id not in user_scripts:
            user_scripts[user_id] = []
        
        if script_id in user_scripts[user_id]:
            embed = discord.Embed(
                title="❌ Already Assigned",
                description=f"User already has access to script: {script['name']}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_scripts[user_id].append(script_id)
        save_user_scripts(user_scripts)
        
        embed = discord.Embed(
            title="✅ Script Assigned Successfully!",
            description=f"Script **{script['name']}** assigned to <@{user_id}>",
            color=0x28a745
        )
        
        embed.add_field(
            name="📄 Details",
            value=f"**Script ID:** {script_id}\n**User ID:** {user_id}\n**Price:** ${script['price']:.2f}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class VerifyPaymentModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Verify Payment")
        
        self.ticket_id = discord.ui.TextInput(
            label="Ticket ID",
            placeholder="Enter ticket ID to verify",
            required=True,
            max_length=10
        )
        
        self.user_id = discord.ui.TextInput(
            label="User ID",
            placeholder="Enter user ID to give buyer role",
            required=True,
            max_length=20
        )
        
        self.add_item(self.ticket_id)
        self.add_item(self.user_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            ticket_id = int(self.ticket_id.value)
            user_id = int(self.user_id.value)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description="Please enter valid ticket ID and user ID",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        tickets = load_tickets()
        ticket = next((t for t in tickets if t['id'] == ticket_id), None)
        
        if not ticket:
            embed = discord.Embed(
                title="❌ Ticket Not Found",
                description=f"No ticket found with ID {ticket_id}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if ticket['status'] == 'verified':
            embed = discord.Embed(
                title="❌ Already Verified",
                description=f"Ticket #{ticket_id} is already verified",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Update ticket status
        ticket['status'] = 'verified'
        ticket['verified_by'] = interaction.user.id
        ticket['verified_at'] = datetime.now().isoformat()
        save_tickets(tickets)
        
        # Give buyer role
        guild = interaction.guild
        user = guild.get_member(user_id)
        if user:
            buyer_role = guild.get_role(BUYER_ROLE_ID)
            if buyer_role and buyer_role not in user.roles:
                await user.add_roles(buyer_role)
        
        embed = discord.Embed(
            title="✅ Payment Verified!",
            description=f"Ticket #{ticket_id} has been verified and buyer role assigned!",
            color=0x28a745
        )
        
        embed.add_field(
            name="📋 Details",
            value=f"**Ticket ID:** #{ticket_id}\n**User:** <@{user_id}>\n**Verified by:** {interaction.user.mention}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class GiveBuyerRoleModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Give Buyer Role")
        
        self.user_id = discord.ui.TextInput(
            label="User ID",
            placeholder="Enter Discord user ID",
            required=True,
            max_length=20
        )
        
        self.add_item(self.user_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = int(self.user_id.value)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid User ID",
                description="Please enter a valid Discord user ID",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild = interaction.guild
        user = guild.get_member(user_id)
        
        if not user:
            embed = discord.Embed(
                title="❌ User Not Found",
                description="User not found in this server",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        buyer_role = guild.get_role(BUYER_ROLE_ID)
        if not buyer_role:
            embed = discord.Embed(
                title="❌ Role Not Found",
                description="Buyer role not found in server",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if buyer_role in user.roles:
            embed = discord.Embed(
                title="❌ Already Has Role",
                description=f"{user.mention} already has the buyer role",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await user.add_roles(buyer_role)
        
        embed = discord.Embed(
            title="✅ Buyer Role Assigned!",
            description=f"Buyer role successfully given to {user.mention}",
            color=0x28a745
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MarketplaceEditorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
    
    @discord.ui.button(label="🚀 Quick Setup", style=discord.ButtonStyle.success, emoji="⚡")
    async def quick_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🚀 Quick Marketplace Setup",
            description="Get your marketplace running in minutes!",
            color=0x28a745
        )
        
        embed.add_field(
            name="1️⃣ Add Sample Scripts",
            value="Create demo scripts to populate your marketplace",
            inline=False
        )
        
        embed.add_field(
            name="2️⃣ Configure Roles",
            value="Set up admin and buyer role permissions",
            inline=False
        )
        
        embed.add_field(
            name="3️⃣ Test Workflow",
            value="Test the complete purchase workflow",
            inline=False
        )
        
        view = QuickSetupView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📚 Script Editor", style=discord.ButtonStyle.primary, emoji="📝")
    async def script_editor(self, interaction: discord.Interaction, button: discord.ui.Button):
        scripts = load_scripts()
        
        embed = discord.Embed(
            title="📚 Advanced Script Editor",
            description="Complete script management system",
            color=0x667eea
        )
        
        if scripts:
            script_list = ""
            for script in scripts[:8]:
                script_list += f"**#{script['id']}** {script['name']} - ${script['price']:.2f} ({script['category']})\n"
            
            embed.add_field(
                name="📋 Current Scripts",
                value=script_list or "No scripts available",
                inline=False
            )
            
            if len(scripts) > 8:
                embed.add_field(
                    name="📊 Total",
                    value=f"Showing 8 of {len(scripts)} scripts",
                    inline=False
                )
        else:
            embed.add_field(
                name="📋 Current Scripts",
                value="No scripts added yet - Start by adding your first script!",
                inline=False
            )
        
        view = AdvancedScriptEditorView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="👥 User Manager", style=discord.ButtonStyle.secondary, emoji="👤")
    async def user_manager(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_scripts = load_user_scripts()
        
        embed = discord.Embed(
            title="👥 Advanced User Manager",
            description="Complete user and permission management",
            color=0x9f7aea
        )
        
        if user_scripts:
            user_list = ""
            for user_id, script_ids in list(user_scripts.items())[:6]:
                try:
                    user = interaction.guild.get_member(int(user_id))
                    username = user.display_name if user else f"User {user_id}"
                    user_list += f"**{username}:** {len(script_ids)} scripts\n"
                except:
                    user_list += f"**User {user_id}:** {len(script_ids)} scripts\n"
            
            embed.add_field(
                name="👤 Users with Scripts",
                value=user_list or "No users with scripts",
                inline=False
            )
        else:
            embed.add_field(
                name="👤 Users with Scripts",
                value="No users have scripts assigned yet",
                inline=False
            )
        
        view = AdvancedUserManagerView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="⚙️ Settings", style=discord.ButtonStyle.secondary, emoji="🔧")
    async def marketplace_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="⚙️ Marketplace Settings",
            description="Configure marketplace behavior and features",
            color=0x6c757d
        )
        
        embed.add_field(
            name="🏷️ Current Role IDs",
            value=f"**Admin Role:** {ADMIN_ROLE_ID}\n**Buyer Role:** {BUYER_ROLE_ID}",
            inline=False
        )
        
        embed.add_field(
            name="📊 Data Files",
            value="**Scripts:** scripts.json\n**Orders:** orders.json\n**Tickets:** tickets.json\n**User Scripts:** user_scripts.json",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Configuration Options",
            value="• Update role IDs\n• Clear all data\n• Export/Import data\n• Reset marketplace",
            inline=False
        )
        
        view = MarketplaceSettingsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📈 Analytics", style=discord.ButtonStyle.success, emoji="📊")
    async def analytics_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        scripts = load_scripts()
        orders = load_orders()
        tickets = load_tickets()
        user_scripts = load_user_scripts()
        
        embed = discord.Embed(
            title="📈 Marketplace Analytics",
            description="Detailed marketplace performance metrics",
            color=0x17a2b8
        )
        
        # Revenue analytics
        total_revenue = sum(order.get('total_price', 0) for order in orders)
        avg_order_value = total_revenue / len(orders) if orders else 0
        
        embed.add_field(
            name="💰 Revenue Analytics",
            value=f"**Total Revenue:** ${total_revenue:.2f}\n**Total Orders:** {len(orders)}\n**Avg Order Value:** ${avg_order_value:.2f}",
            inline=True
        )
        
        # Script analytics
        if scripts:
            avg_price = sum(s['price'] for s in scripts) / len(scripts)
            most_expensive = max(scripts, key=lambda x: x['price'])
            embed.add_field(
                name="📚 Script Analytics",
                value=f"**Total Scripts:** {len(scripts)}\n**Avg Price:** ${avg_price:.2f}\n**Most Expensive:** {most_expensive['name']} (${most_expensive['price']:.2f})",
                inline=True
            )
        
        # User analytics
        total_script_assignments = sum(len(scripts) for scripts in user_scripts.values())
        avg_scripts_per_user = total_script_assignments / len(user_scripts) if user_scripts else 0
        
        embed.add_field(
            name="👥 User Analytics",
            value=f"**Active Users:** {len(user_scripts)}\n**Total Assignments:** {total_script_assignments}\n**Avg Scripts/User:** {avg_scripts_per_user:.1f}",
            inline=True
        )
        
        # Recent activity
        recent_orders = len([o for o in orders if o.get('created_at', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
        pending_tickets = len([t for t in tickets if t.get('status') == 'pending'])
        
        embed.add_field(
            name="📊 Recent Activity",
            value=f"**Today's Orders:** {recent_orders}\n**Pending Tickets:** {pending_tickets}\n**Verification Rate:** {((len(tickets) - pending_tickets) / len(tickets) * 100) if tickets else 0:.1f}%",
            inline=False
        )
        
        embed.set_footer(text="Analytics Dashboard | Real-time Data")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class QuickSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📚 Add Sample Scripts", style=discord.ButtonStyle.success, emoji="⚡")
    async def add_sample_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        scripts = load_scripts()
        
        sample_scripts = [
            {
                'id': len(scripts) + 1,
                'name': 'Discord Moderation Bot',
                'description': 'Advanced Discord bot with auto-moderation, role management, and logging features.',
                'price': 29.99,
                'category': 'Discord Bots',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': len(scripts) + 2,
                'name': 'Web Scraper Pro',
                'description': 'Professional web scraping tool with proxy support and data export.',
                'price': 19.99,
                'category': 'Automation',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': len(scripts) + 3,
                'name': 'Trading Bot Starter',
                'description': 'Cryptocurrency trading bot with basic strategies and backtesting.',
                'price': 49.99,
                'category': 'Trading',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': len(scripts) + 4,
                'name': 'Game Automation Suite',
                'description': 'Collection of game automation scripts for popular online games.',
                'price': 15.99,
                'category': 'Gaming',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        scripts.extend(sample_scripts)
        save_scripts(scripts)
        
        embed = discord.Embed(
            title="✅ Sample Scripts Added!",
            description="4 sample scripts have been added to your marketplace!",
            color=0x28a745
        )
        
        script_list = ""
        for script in sample_scripts:
            script_list += f"• **{script['name']}** - ${script['price']:.2f} ({script['category']})\n"
        
        embed.add_field(
            name="📚 Added Scripts",
            value=script_list,
            inline=False
        )
        
        embed.add_field(
            name="🎯 Next Steps",
            value="1. Test the `/shop` command\n2. Configure user roles\n3. Test the purchase workflow",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🏷️ Configure Roles", style=discord.ButtonStyle.primary, emoji="👑")
    async def configure_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        admin_role = guild.get_role(ADMIN_ROLE_ID)
        buyer_role = guild.get_role(BUYER_ROLE_ID)
        
        embed = discord.Embed(
            title="🏷️ Role Configuration",
            description="Current role setup and configuration options",
            color=0x667eea
        )
        
        embed.add_field(
            name="👑 Admin Role",
            value=f"**ID:** {ADMIN_ROLE_ID}\n**Status:** {'✅ Found' if admin_role else '❌ Not Found'}\n**Name:** {admin_role.name if admin_role else 'Unknown'}",
            inline=True
        )
        
        embed.add_field(
            name="🎫 Buyer Role",
            value=f"**ID:** {BUYER_ROLE_ID}\n**Status:** {'✅ Found' if buyer_role else '❌ Not Found'}\n**Name:** {buyer_role.name if buyer_role else 'Unknown'}",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Configuration",
            value="To update role IDs, edit the following lines in the bot code:\n```python\nADMIN_ROLE_ID = YOUR_ADMIN_ROLE_ID\nBUYER_ROLE_ID = YOUR_BUYER_ROLE_ID\n```",
            inline=False
        )
        
        embed.add_field(
            name="📋 Role Permissions",
            value="**Admin Role:** Full marketplace management\n**Buyer Role:** Access to purchased scripts via `/get_scripts`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🧪 Test Workflow", style=discord.ButtonStyle.secondary, emoji="🔬")
    async def test_workflow(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🧪 Test Marketplace Workflow",
            description="Complete testing guide for your marketplace",
            color=0x9f7aea
        )
        
        embed.add_field(
            name="1️⃣ Test Shop Command",
            value="Use `/shop` to browse scripts and test the cart system",
            inline=False
        )
        
        embed.add_field(
            name="2️⃣ Test Purchase Flow",
            value="1. Add scripts to cart\n2. Go through checkout\n3. Check order creation",
            inline=False
        )
        
        embed.add_field(
            name="3️⃣ Test Admin Functions",
            value="1. Verify payment with `/edit`\n2. Assign scripts to users\n3. Give buyer role",
            inline=False
        )
        
        embed.add_field(
            name="4️⃣ Test User Access",
            value="1. Give yourself buyer role\n2. Use `/get_scripts` command\n3. Download assigned scripts",
            inline=False
        )
        
        embed.add_field(
            name="✅ Validation Checklist",
            value="• Shop displays correctly ✓\n• Cart system works ✓\n• Orders are created ✓\n• Payment verification works ✓\n• Script access works ✓",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AdvancedScriptEditorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="➕ Add Script", style=discord.ButtonStyle.success, emoji="📝")
    async def add_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddScriptModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="✏️ Edit Script", style=discord.ButtonStyle.primary, emoji="📝")
    async def edit_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EditScriptModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Delete Script", style=discord.ButtonStyle.danger, emoji="❌")
    async def delete_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DeleteScriptModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Bulk Actions", style=discord.ButtonStyle.secondary, emoji="📊")
    async def bulk_actions(self, interaction: discord.Interaction, button: discord.ui.Button):
        scripts = load_scripts()
        
        embed = discord.Embed(
            title="📋 Bulk Script Actions",
            description="Perform actions on multiple scripts",
            color=0x6c757d
        )
        
        if scripts:
            embed.add_field(
                name="📊 Current Data",
                value=f"**Total Scripts:** {len(scripts)}\n**Categories:** {len(set(s['category'] for s in scripts))}\n**Total Value:** ${sum(s['price'] for s in scripts):.2f}",
                inline=False
            )
        
        view = BulkScriptActionsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class AdvancedUserManagerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="➕ Assign Script", style=discord.ButtonStyle.success, emoji="📋")
    async def assign_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AssignScriptModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="👤 View User", style=discord.ButtonStyle.primary, emoji="👥")
    async def view_user_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ViewUserScriptsModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Remove Access", style=discord.ButtonStyle.danger, emoji="❌")
    async def remove_user_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RemoveUserScriptsModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏷️ Manage Roles", style=discord.ButtonStyle.secondary, emoji="🎫")
    async def manage_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = RoleManagementView()
        
        embed = discord.Embed(
            title="🏷️ Role Management",
            description="Manage user roles and permissions",
            color=0x9f7aea
        )
        
        embed.add_field(
            name="🎫 Available Actions",
            value="• Give buyer role to users\n• Remove buyer role\n• View role assignments\n• Bulk role operations",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class BulkScriptActionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📊 Export Scripts", style=discord.ButtonStyle.primary, emoji="💾")
    async def export_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        scripts = load_scripts()
        
        if not scripts:
            await interaction.response.send_message("❌ No scripts to export!", ephemeral=True)
            return
        
        script_text = "**Marketplace Scripts Export**\n\n"
        for script in scripts:
            script_text += f"**ID {script['id']}:** {script['name']}\n"
            script_text += f"**Price:** ${script['price']:.2f}\n"
            script_text += f"**Category:** {script['category']}\n"
            script_text += f"**Description:** {script['description']}\n"
            script_text += f"**Created:** {script['created_at'][:10]}\n\n"
        
        # Discord has character limits, so we'll create a summary
        embed = discord.Embed(
            title="📊 Scripts Export",
            description=f"Export of {len(scripts)} marketplace scripts",
            color=0x28a745
        )
        
        # Group by category
        categories = {}
        for script in scripts:
            cat = script['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(script)
        
        for category, cat_scripts in categories.items():
            script_list = ""
            for script in cat_scripts:
                script_list += f"• {script['name']} (${script['price']:.2f})\n"
            
            embed.add_field(
                name=f"📁 {category}",
                value=script_list,
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 Update Prices", style=discord.ButtonStyle.secondary, emoji="💰")
    async def bulk_price_update(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BulkPriceUpdateModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Clear All", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def clear_all_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        scripts = load_scripts()
        
        if not scripts:
            await interaction.response.send_message("❌ No scripts to clear!", ephemeral=True)
            return
        
        view = ConfirmClearView("scripts")
        
        embed = discord.Embed(
            title="⚠️ Clear All Scripts",
            description=f"Are you sure you want to delete ALL {len(scripts)} scripts?\n\n**This action cannot be undone!**",
            color=0xff0000
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class RoleManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🎫 Give Buyer Role", style=discord.ButtonStyle.success, emoji="➕")
    async def give_buyer_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GiveBuyerRoleModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="❌ Remove Buyer Role", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def remove_buyer_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RemoveBuyerRoleModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="👥 View Role Members", style=discord.ButtonStyle.primary, emoji="📋")
    async def view_role_members(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        buyer_role = guild.get_role(BUYER_ROLE_ID)
        admin_role = guild.get_role(ADMIN_ROLE_ID)
        
        embed = discord.Embed(
            title="👥 Role Members",
            description="Current role assignments",
            color=0x667eea
        )
        
        if buyer_role:
            buyer_members = [member.display_name for member in buyer_role.members[:10]]
            embed.add_field(
                name=f"🎫 {buyer_role.name} ({len(buyer_role.members)})",
                value="\n".join(buyer_members) if buyer_members else "No members",
                inline=True
            )
        
        if admin_role:
            admin_members = [member.display_name for member in admin_role.members[:10]]
            embed.add_field(
                name=f"👑 {admin_role.name} ({len(admin_role.members)})",
                value="\n".join(admin_members) if admin_members else "No members",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MarketplaceSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🗑️ Clear All Data", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def clear_all_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ConfirmClearView("all_data")
        
        embed = discord.Embed(
            title="⚠️ Clear All Marketplace Data",
            description="This will delete:\n• All scripts\n• All orders\n• All tickets\n• All user assignments\n\n**This action cannot be undone!**",
            color=0xff0000
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📊 Backup Data", style=discord.ButtonStyle.primary, emoji="💾")
    async def backup_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        scripts = load_scripts()
        orders = load_orders()
        tickets = load_tickets()
        user_scripts = load_user_scripts()
        
        backup_info = {
            'scripts': len(scripts),
            'orders': len(orders),
            'tickets': len(tickets),
            'user_assignments': len(user_scripts),
            'total_revenue': sum(order.get('total_price', 0) for order in orders),
            'backup_date': datetime.now().isoformat()
        }
        
        embed = discord.Embed(
            title="💾 Data Backup Summary",
            description="Current marketplace data summary",
            color=0x28a745
        )
        
        embed.add_field(
            name="📊 Data Counts",
            value=f"**Scripts:** {backup_info['scripts']}\n**Orders:** {backup_info['orders']}\n**Tickets:** {backup_info['tickets']}\n**User Assignments:** {backup_info['user_assignments']}",
            inline=True
        )
        
        embed.add_field(
            name="💰 Financial Data",
            value=f"**Total Revenue:** ${backup_info['total_revenue']:.2f}\n**Avg Order Value:** ${backup_info['total_revenue'] / max(backup_info['orders'], 1):.2f}",
            inline=True
        )
        
        embed.add_field(
            name="📅 Backup Info",
            value=f"**Date:** {backup_info['backup_date'][:10]}\n**Time:** {backup_info['backup_date'][11:19]}\n**Status:** Ready for backup",
            inline=False
        )
        
        embed.set_footer(text="Data files: scripts.json, orders.json, tickets.json, user_scripts.json")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ConfirmClearView(discord.ui.View):
    def __init__(self, data_type):
        super().__init__(timeout=60)
        self.data_type = data_type
    
    @discord.ui.button(label="✅ Confirm Delete", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def confirm_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.data_type == "scripts":
            save_scripts([])
            message = "All scripts have been deleted!"
        elif self.data_type == "all_data":
            save_scripts([])
            save_orders([])
            save_tickets([])
            save_user_scripts({})
            message = "All marketplace data has been cleared!"
        
        embed = discord.Embed(
            title="✅ Data Cleared",
            description=message,
            color=0x28a745
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary, emoji="🚫")
    async def cancel_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Operation Cancelled",
            description="No data was deleted.",
            color=0x6c757d
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

# Additional modal classes for the new functionality
class BulkPriceUpdateModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Bulk Price Update")
        
        self.percentage = discord.ui.TextInput(
            label="Price Change Percentage",
            placeholder="e.g., 10 for +10%, -20 for -20%",
            required=True,
            max_length=10
        )
        
        self.category = discord.ui.TextInput(
            label="Category (optional)",
            placeholder="Leave empty to update all scripts",
            required=False,
            max_length=50
        )
        
        self.add_item(self.percentage)
        self.add_item(self.category)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            percentage = float(self.percentage.value)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Percentage",
                description="Please enter a valid percentage (e.g., 10, -20)",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        scripts = load_scripts()
        updated_count = 0
        
        for script in scripts:
            if not self.category.value or script['category'].lower() == self.category.value.lower():
                old_price = script['price']
                script['price'] = round(old_price * (1 + percentage / 100), 2)
                updated_count += 1
        
        save_scripts(scripts)
        
        embed = discord.Embed(
            title="✅ Prices Updated!",
            description=f"Updated {updated_count} script prices by {percentage:+.1f}%",
            color=0x28a745
        )
        
        if self.category.value:
            embed.add_field(
                name="📁 Category Filter",
                value=f"Only updated scripts in category: {self.category.value}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RemoveBuyerRoleModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Remove Buyer Role")
        
        self.user_id = discord.ui.TextInput(
            label="User ID",
            placeholder="Enter Discord user ID",
            required=True,
            max_length=20
        )
        
        self.add_item(self.user_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = int(self.user_id.value)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid User ID",
                description="Please enter a valid Discord user ID",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild = interaction.guild
        user = guild.get_member(user_id)
        
        if not user:
            embed = discord.Embed(
                title="❌ User Not Found",
                description="User not found in this server",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        buyer_role = guild.get_role(BUYER_ROLE_ID)
        if not buyer_role:
            embed = discord.Embed(
                title="❌ Role Not Found",
                description="Buyer role not found in server",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if buyer_role not in user.roles:
            embed = discord.Embed(
                title="❌ Role Not Assigned",
                description=f"{user.mention} doesn't have the buyer role",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await user.remove_roles(buyer_role)
        
        embed = discord.Embed(
            title="✅ Buyer Role Removed!",
            description=f"Buyer role successfully removed from {user.mention}",
            color=0x28a745
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class EditScriptModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Edit Existing Script")
        
        self.script_id = discord.ui.TextInput(
            label="Script ID to Edit",
            placeholder="Enter the script ID number",
            required=True,
            max_length=10
        )
        
        self.new_name = discord.ui.TextInput(
            label="New Script Name (optional)",
            placeholder="Leave empty to keep current name",
            required=False,
            max_length=100
        )
        
        self.new_price = discord.ui.TextInput(
            label="New Price (optional)",
            placeholder="Leave empty to keep current price",
            required=False,
            max_length=10
        )
        
        self.new_description = discord.ui.TextInput(
            label="New Description (optional)",
            placeholder="Leave empty to keep current description",
            required=False,
            style=discord.TextStyle.long,
            max_length=1000
        )
        
        self.add_item(self.script_id)
        self.add_item(self.new_name)
        self.add_item(self.new_price)
        self.add_item(self.new_description)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            script_id = int(self.script_id.value)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid ID",
                description="Please enter a valid script ID number",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        scripts = load_scripts()
        script_to_edit = next((script for script in scripts if script['id'] == script_id), None)
        
        if not script_to_edit:
            embed = discord.Embed(
                title="❌ Script Not Found",
                description=f"No script found with ID {script_id}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        changes = []
        
        if self.new_name.value:
            old_name = script_to_edit['name']
            script_to_edit['name'] = self.new_name.value
            changes.append(f"Name: {old_name} → {self.new_name.value}")
        
        if self.new_price.value:
            try:
                new_price = float(self.new_price.value)
                old_price = script_to_edit['price']
                script_to_edit['price'] = new_price
                changes.append(f"Price: ${old_price:.2f} → ${new_price:.2f}")
            except ValueError:
                pass
        
        if self.new_description.value:
            script_to_edit['description'] = self.new_description.value
            changes.append("Description updated")
        
        if changes:
            save_scripts(scripts)
            embed = discord.Embed(
                title="✅ Script Updated Successfully!",
                description=f"**{script_to_edit['name']}** has been updated!",
                color=0x28a745
            )
            
            embed.add_field(
                name="📝 Changes Made",
                value="\n".join(changes),
                inline=False
            )
        else:
            embed = discord.Embed(
                title="⚠️ No Changes Made",
                description="No fields were provided to update",
                color=0xffa500
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class DeleteScriptModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Delete Script")
        
        self.script_id = discord.ui.TextInput(
            label="Script ID to Delete",
            placeholder="Enter the script ID number",
            required=True,
            max_length=10
        )
        
        self.add_item(self.script_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            script_id = int(self.script_id.value)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid ID",
                description="Please enter a valid script ID number",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        scripts = load_scripts()
        script_to_delete = None
        
        for i, script in enumerate(scripts):
            if script['id'] == script_id:
                script_to_delete = scripts.pop(i)
                break
        
        if script_to_delete:
            save_scripts(scripts)
            embed = discord.Embed(
                title="✅ Script Deleted",
                description=f"**{script_to_delete['name']}** has been deleted from the shop!",
                color=0x28a745
            )
        else:
            embed = discord.Embed(
                title="❌ Script Not Found",
                description=f"No script found with ID {script_id}",
                color=0xff0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ViewUserScriptsModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="View User Scripts")
        
        self.user_id = discord.ui.TextInput(
            label="User ID",
            placeholder="Enter user ID to view their scripts",
            required=True,
            max_length=20
        )
        
        self.add_item(self.user_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        user_scripts = load_user_scripts()
        user_id = self.user_id.value
        
        if user_id not in user_scripts:
            embed = discord.Embed(
                title="❌ User Not Found",
                description=f"User ID {user_id} has no assigned scripts.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        scripts = load_scripts()
        user_script_ids = user_scripts[user_id]
        
        embed = discord.Embed(
            title=f"👤 User Scripts - {user_id}",
            description=f"Scripts assigned to <@{user_id}>:",
            color=0x667eea
        )
        
        for script_id in user_script_ids:
            script = next((s for s in scripts if s['id'] == script_id), None)
            if script:
                embed.add_field(
                    name=f"📄 {script['name']}",
                    value=f"**ID:** {script_id}\n**Category:** {script['category']}\n**Price:** ${script['price']:.2f}",
                    inline=True
                )
        
        embed.set_footer(text=f"Total scripts: {len(user_script_ids)}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RemoveUserScriptsModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Remove User Scripts")
        
        self.user_id = discord.ui.TextInput(
            label="User ID",
            placeholder="Enter user ID",
            required=True,
            max_length=20
        )
        
        self.script_id = discord.ui.TextInput(
            label="Script ID (optional)",
            placeholder="Leave empty to remove all scripts",
            required=False,
            max_length=10
        )
        
        self.add_item(self.user_id)
        self.add_item(self.script_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        user_scripts = load_user_scripts()
        user_id = self.user_id.value
        
        if user_id not in user_scripts:
            embed = discord.Embed(
                title="❌ User Not Found",
                description=f"User ID {user_id} has no assigned scripts.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if self.script_id.value:
            # Remove specific script
            try:
                script_id = int(self.script_id.value)
                if script_id in user_scripts[user_id]:
                    user_scripts[user_id].remove(script_id)
                    if not user_scripts[user_id]:
                        del user_scripts[user_id]
                    save_user_scripts(user_scripts)
                    
                    embed = discord.Embed(
                        title="✅ Script Removed",
                        description=f"Script ID {script_id} removed from user {user_id}",
                        color=0x28a745
                    )
                else:
                    embed = discord.Embed(
                        title="❌ Script Not Found",
                        description=f"User doesn't have script ID {script_id}",
                        color=0xff0000
                    )
            except ValueError:
                embed = discord.Embed(
                    title="❌ Invalid Script ID",
                    description="Please enter a valid script ID number",
                    color=0xff0000
                )
        else:
            # Remove all scripts
            del user_scripts[user_id]
            save_user_scripts(user_scripts)
            
            embed = discord.Embed(
                title="✅ All Scripts Removed",
                description=f"All scripts removed from user {user_id}",
                color=0x28a745
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Include the shop view classes from original code
class PublicShopView(discord.ui.View):
    def __init__(self, scripts):
        super().__init__(timeout=None)  # Persistent view
        self.scripts = scripts
    
    @discord.ui.button(label="Browse Shop", style=discord.ButtonStyle.primary, emoji="🛍️")
    async def browse_shop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open personal shopping interface - admin only"""
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ You need administrator permissions to access the shop!", ephemeral=True)
            return
        # Create personal shop embed
        embed = discord.Embed(
            title="Your Personal Shop",
            description="Welcome to your personal shopping interface! Select scripts from the dropdown and add them to your cart.",
            color=0x667eea,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Your Cart",
            value="Empty - Start adding scripts!",
            inline=False
        )
        
        embed.set_footer(text="Personal Shop Interface | Only visible to you", icon_url=bot.user.avatar.url if bot.user.avatar else None)
        
        # Create personal shop view with cart
        view = ShopView(self.scripts, [])
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self, scripts, cart):
        super().__init__(timeout=600)
        self.scripts = scripts
        self.cart = cart
        self.current_page = 0
        self.scripts_per_page = 10
        
        self.update_buttons()
    
    def update_buttons(self):
        self.clear_items()
        
        total_pages = (len(self.scripts) + self.scripts_per_page - 1) // self.scripts_per_page
        start_idx = self.current_page * self.scripts_per_page
        end_idx = min(start_idx + self.scripts_per_page, len(self.scripts))
        current_scripts = self.scripts[start_idx:end_idx]
        
        # Add script selection dropdown
        script_select = ScriptSelectMenu(current_scripts, self.cart)
        self.add_item(script_select)
        
        # Add to cart button
        add_to_cart_button = discord.ui.Button(
            label="Add Selected to Cart",
            style=discord.ButtonStyle.success,
            emoji="🛒"
        )
        add_to_cart_button.callback = self.add_selected_to_cart
        self.add_item(add_to_cart_button)
        
        # Navigation buttons
        if total_pages > 1:
            prev_button = discord.ui.Button(
                label="Previous",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page == 0
            )
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
            
            next_button = discord.ui.Button(
                label="Next", 
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page >= total_pages - 1
            )
            next_button.callback = self.next_page
            self.add_item(next_button)
        
        # Cart and checkout buttons
        cart_button = discord.ui.Button(
            label=f"View Cart ({len(self.cart)})",
            style=discord.ButtonStyle.primary
        )
        cart_button.callback = self.view_cart
        self.add_item(cart_button)
        
        if self.cart:
            checkout_button = discord.ui.Button(
                label="Checkout",
                style=discord.ButtonStyle.success
            )
            checkout_button.callback = self.checkout
            self.add_item(checkout_button)
    
    async def previous_page(self, interaction: discord.Interaction):
        self.current_page -= 1
        self.update_buttons()
        await self.update_shop_embed(interaction)
    
    async def next_page(self, interaction: discord.Interaction):
        self.current_page += 1
        self.update_buttons()
        await self.update_shop_embed(interaction)
    
    async def update_shop_embed(self, interaction: discord.Interaction):
        start_idx = self.current_page * self.scripts_per_page
        end_idx = min(start_idx + self.scripts_per_page, len(self.scripts))
        current_scripts = self.scripts[start_idx:end_idx]
        
        embed = discord.Embed(
            title="Script Shop",
            description="Premium scripts for your projects. Select scripts from the dropdown and click 'Add Selected to Cart'!",
            color=0x667eea,
            timestamp=datetime.now()
        )
        
        # Show available scripts in a clean list format
        scripts_text = ""
        for script in current_scripts:
            in_cart = "[IN CART] " if script['id'] in [s['id'] for s in self.cart] else ""
            scripts_text += f"**{in_cart}{script['name']}** - ${script['price']:.2f} ({script['category']})\n"
        
        embed.add_field(
            name="Available Scripts",
            value=scripts_text or "No scripts available",
            inline=False
        )
        
        if self.cart:
            total_price = sum(item['price'] for item in self.cart)
            cart_items = ", ".join([item['name'] for item in self.cart])
            embed.add_field(
                name="Your Cart",
                value=f"**Items:** {cart_items}\n**Total:** ${total_price:.2f}",
                inline=False
            )
        else:
            embed.add_field(
                name="Your Cart",
                value="Empty - Start adding scripts!",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.current_page + 1}/{(len(self.scripts) + self.scripts_per_page - 1) // self.scripts_per_page} | Use dropdown to select scripts")
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def view_cart(self, interaction: discord.Interaction):
        if not self.cart:
            embed = discord.Embed(
                title="🛒 Your Cart",
                description="Your cart is empty!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🛒 Your Cart",
            description="Items in your cart:",
            color=0x28a745
        )
        
        total_price = 0
        for item in self.cart:
            embed.add_field(
                name=item['name'],
                value=f"💰 ${item['price']:.2f}\n📁 {item['category']}",
                inline=True
            )
            total_price += item['price']
        
        embed.add_field(
            name="💰 Total Price",
            value=f"${total_price:.2f}",
            inline=False
        )
        
        view = CartView(self.cart, self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def add_selected_to_cart(self, interaction: discord.Interaction):
        # Get the selected scripts from the select menu
        script_select = None
        for item in self.children:
            if isinstance(item, ScriptSelectMenu):
                script_select = item
                break
        
        if not script_select or not script_select.values:
            await interaction.response.send_message("Please select at least one script to add to cart!", ephemeral=True)
            return
        
        added_scripts = []
        for script_id in script_select.values:
            script_id_int = int(script_id)
            script = next((s for s in self.scripts if s['id'] == script_id_int), None)
            if script and not any(item['id'] == script_id_int for item in self.cart):
                self.cart.append(script)
                added_scripts.append(script['name'])
        
        if added_scripts:
            self.update_buttons()
            await self.update_shop_embed(interaction)
            
            # Send confirmation message
            added_names = ", ".join(added_scripts)
            await interaction.followup.send(f"Added to cart: {added_names}", ephemeral=True)
        else:
            await interaction.response.send_message("Selected scripts are already in your cart!", ephemeral=True)
    
    async def checkout(self, interaction: discord.Interaction):
        if not self.cart:
            await interaction.response.send_message("Your cart is empty!", ephemeral=True)
            return
        
        modal = CheckoutModal(self.cart)
        await interaction.response.send_modal(modal)

class ScriptSelectMenu(discord.ui.Select):
    def __init__(self, scripts, cart):
        self.scripts = scripts
        self.cart = cart
        
        # Create options for the select menu
        options = []
        for script in scripts:
            in_cart = any(item['id'] == script['id'] for item in cart)
            label = f"{script['name']} - ${script['price']:.2f}"
            if in_cart:
                label = f"[IN CART] {label}"
            
            description = f"{script['category']} - {script['description'][:50]}{'...' if len(script['description']) > 50 else ''}"
            
            options.append(discord.SelectOption(
                label=label[:100],  # Discord limit
                value=str(script['id']),
                description=description[:100],  # Discord limit
                emoji="🛒" if not in_cart else "✅"
            ))
        
        super().__init__(
            placeholder="Select scripts to add to cart...",
            min_values=0,
            max_values=min(len(options), 25),  # Discord limit
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        # This will be handled by the add_selected_to_cart method
        await interaction.response.defer()

class CartView(discord.ui.View):
    def __init__(self, cart, shop_view):
        super().__init__(timeout=300)
        self.cart = cart
        self.shop_view = shop_view
    
    @discord.ui.button(label="Clear Cart", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def clear_cart(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.shop_view.cart.clear()
        embed = discord.Embed(
            title="Cart Cleared",
            description="Your cart has been cleared!",
            color=0xff0000
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="Proceed to Checkout", style=discord.ButtonStyle.success, emoji="💳")
    async def proceed_checkout(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CheckoutModal(self.cart)
        await interaction.response.send_modal(modal)

class CheckoutModal(discord.ui.Modal):
    def __init__(self, cart):
        super().__init__(title="Checkout - Complete Purchase")
        self.cart = cart
        
        self.email = discord.ui.TextInput(
            label="Email Address",
            placeholder="your.email@example.com",
            required=True,
            max_length=100
        )
        
        self.discord_user = discord.ui.TextInput(
            label="Discord Username",
            placeholder="YourUsername#1234",
            required=True,
            max_length=50
        )
        
        self.add_item(self.email)
        self.add_item(self.discord_user)
    
    async def on_submit(self, interaction: discord.Interaction):
        orders = load_orders()
        total_price = sum(item['price'] for item in self.cart)
        
        order = {
            'id': len(orders) + 1,
            'items': self.cart,
            'buyer_email': self.email.value,
            'buyer_discord': self.discord_user.value,
            'buyer_id': interaction.user.id,
            'total_price': total_price,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        orders.append(order)
        save_orders(orders)
        
        # Create ticket for payment verification
        tickets = load_tickets()
        ticket = {
            'id': len(tickets) + 1,
            'order_id': order['id'],
            'user_id': interaction.user.id,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        tickets.append(ticket)
        save_tickets(tickets)
        
        embed = discord.Embed(
            title="✅ Order Placed Successfully!",
            description=f"Your order has been placed!",
            color=0x28a745
        )
        
        items_text = "\n".join([f"• {item['name']} - ${item['price']:.2f}" for item in self.cart])
        
        embed.add_field(
            name="📧 Order Details",
            value=f"**Order ID:** #{order['id']}\n**Ticket ID:** #{ticket['id']}\n**Items:**\n{items_text}\n**Total:** ${total_price:.2f}",
            inline=False
        )
        
        embed.add_field(
            name="📞 Next Steps",
            value="1. Contact an admin with your order details\n2. Send payment proof\n3. Wait for verification\n4. Get buyer role and script access!",
            inline=False
        )
        
        embed.set_footer(text="Thank you for your purchase! | ScriptHub")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Get scripts command for buyers (keep from original)
@bot.tree.command(name='get_scripts_panel', description='Create a permanent Get Scripts panel for this channel (Admin only)')
async def get_scripts_panel(interaction: discord.Interaction):
    """Create a permanent panel in channel for users to get their scripts"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You need administrator permissions to create a scripts panel!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📦 Get Your Scripts",
        description="Click the button below to receive your purchased scripts via DM!",
        color=0x28a745
    )
    
    embed.add_field(
        name="🎫 Requirements",
        value="• Must have the Buyer role\n• Must have purchased scripts\n• Scripts will be sent via DM",
        inline=False
    )
    
    embed.add_field(
        name="📞 Support",
        value="If you're having issues accessing your scripts, contact an administrator.",
        inline=False
    )
    
    embed.set_footer(text="Scripts Panel | Click button to access your purchased scripts")
    
    view = GetScriptsPanelView()
    await interaction.response.send_message(embed=embed, view=view)

class GetScriptsPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
    
    @discord.ui.button(label="📥 Get My Scripts", style=discord.ButtonStyle.success, emoji="📦", custom_id="get_scripts_button")
    async def get_my_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Send user's scripts via DM - admin only"""
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ You need administrator permissions to access scripts!", ephemeral=True)
            return
        
        user_scripts = load_user_scripts()
        user_id = str(interaction.user.id)
        
        if user_id not in user_scripts or not user_scripts[user_id]:
            await interaction.response.send_message("📦 No scripts available for you yet.\nContact an admin if you believe this is an error.", ephemeral=True)
            return
        
        scripts = load_scripts()
        user_script_ids = user_scripts[user_id]
        
        # Try to send DM
        try:
            dm_embed = discord.Embed(
                title="📦 Your Purchased Scripts",
                description=f"Here are your {len(user_script_ids)} purchased scripts:",
                color=0x28a745,
                timestamp=datetime.now()
            )
            
            dm_embed.set_footer(text="Zpofe's Script Shop | Your Personal Scripts")
            
            # Create script buttons for DM
            dm_view = UserScriptsDMView(user_script_ids, scripts)
            
            # Add script details to embed
            for script_id in user_script_ids:
                script = next((s for s in scripts if s['id'] == script_id), None)
                if script:
                    dm_embed.add_field(
                        name=f"📄 {script['name']}",
                        value=f"**Category:** {script['category']}\n**Description:** {script['description'][:100]}{'...' if len(script['description']) > 100 else ''}",
                        inline=False
                    )
            
            await interaction.user.send(embed=dm_embed, view=dm_view)
            
            # Confirm in channel
            await interaction.response.send_message("✅ Your scripts have been sent to your DMs! Check your direct messages.", ephemeral=True)
            
        except discord.Forbidden:
            # If DM fails, send ephemeral message with scripts
            embed = discord.Embed(
                title="📦 Your Scripts (DMs Disabled)",
                description="Your scripts are listed below since DMs are disabled:",
                color=0xffa500
            )
            
            for script_id in user_script_ids:
                script = next((s for s in scripts if s['id'] == script_id), None)
                if script:
                    embed.add_field(
                        name=f"📄 {script['name']}",
                        value=f"**Category:** {script['category']}\n**Price:** ${script['price']:.2f}",
                        inline=True
                    )
            
            embed.add_field(
                name="📞 Getting Your Files",
                value="Contact an admin to receive your script files since DMs are disabled.",
                inline=False
            )
            
            view = UserScriptsView(user_script_ids, scripts)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class UserScriptsDMView(discord.ui.View):
    def __init__(self, script_ids, scripts):
        super().__init__(timeout=600)
        self.script_ids = script_ids
        self.scripts = scripts
        
        # Add buttons for each script (max 25 components)
        for script_id in script_ids[:20]:  # Limit to 20 scripts
            script = next((s for s in scripts if s['id'] == script_id), None)
            if script:
                button = ScriptDMDownloadButton(script)
                self.add_item(button)

class ScriptDMDownloadButton(discord.ui.Button):
    def __init__(self, script):
        self.script = script
        super().__init__(
            label=f"📥 {script['name'][:20]}{'...' if len(script['name']) > 20 else ''}",
            style=discord.ButtonStyle.success,
            emoji="📥"
        )
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"📥 {self.script['name']}",
            description="Your script is ready for download!",
            color=0x28a745,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📄 Script Details",
            value=f"**Name:** {self.script['name']}\n**Category:** {self.script['category']}\n**Value:** ${self.script['price']:.2f}",
            inline=False
        )
        
        embed.add_field(
            name="📋 Description",
            value=self.script['description'],
            inline=False
        )
        
        embed.add_field(
            name="📎 Script File",
            value="**Important:** This is a demo response. In production, the actual script file would be attached here or provided as a download link.\n\n*Contact the admin to receive your actual script file.*",
            inline=False
        )
        
        embed.add_field(
            name="📞 Support",
            value="If you need help with this script or have questions, contact our support team!",
            inline=False
        )
        
        embed.set_footer(text="Zpofe's Script Shop | Script Download")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='get_scripts', description='Get your purchased scripts (Admin only)')
async def get_scripts(interaction: discord.Interaction):
    """Allow admins to get scripts"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You need administrator permissions to access this command!", ephemeral=True)
        return
    
    user_scripts = load_user_scripts()
    user_id = str(interaction.user.id)
    
    if user_id not in user_scripts or not user_scripts[user_id]:
        embed = discord.Embed(
            title="📦 No Scripts Available",
            description="You don't have any scripts assigned to you yet.\nContact an admin if you believe this is an error.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📦 Your Scripts",
        description="Here are the scripts you have access to:",
        color=0x28a745
    )
    
    scripts = load_scripts()
    user_script_ids = user_scripts[user_id]
    
    # Create buttons for each script
    view = UserScriptsView(user_script_ids, scripts)
    
    for script_id in user_script_ids:
        script = next((s for s in scripts if s['id'] == script_id), None)
        if script:
            embed.add_field(
                name=f"📄 {script['name']}",
                value=f"**Category:** {script['category']}\n**Price:** ${script['price']:.2f}",
                inline=True
            )
    
    embed.set_footer(text="Click the buttons below to get your script files")
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class UserScriptsView(discord.ui.View):
    def __init__(self, script_ids, scripts):
        super().__init__(timeout=300)
        self.script_ids = script_ids
        self.scripts = scripts
        
        for script_id in script_ids[:5]:  # Max 5 buttons per row
            script = next((s for s in scripts if s['id'] == script_id), None)
            if script:
                button = ScriptDownloadButton(script)
                self.add_item(button)

class ScriptDownloadButton(discord.ui.Button):
    def __init__(self, script):
        self.script = script
        super().__init__(
            label=f"Get {script['name']}",
            style=discord.ButtonStyle.success,
            emoji="📥"
        )
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"📥 {self.script['name']}",
            description="Here's your script!",
            color=0x28a745
        )
        
        embed.add_field(
            name="📄 Script Details",
            value=f"**Name:** {self.script['name']}\n**Category:** {self.script['category']}\n**Description:** {self.script['description']}",
            inline=False
        )
        
        embed.add_field(
            name="📞 Support",
            value="If you need help with this script, contact our support team!",
            inline=False
        )
        
        # In a real implementation, you would send the actual script file here
        embed.add_field(
            name="📎 Script File",
            value="*Script file would be attached here or sent via DM*\n\n**Note:** This is a demo - contact an admin to get your actual script file.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Run the bot
if __name__ == "__main__":
    print("Starting Discord Script Shop Bot...")
    print("🔧 Checking environment variables...")
    
    # Check bot token
    bot_token = os.getenv('BOT_TOKEN') or os.getenv('bot_token')
    if not bot_token:
        print("❌ Bot token environment variable not found!")
        print("Please add your Discord bot token as a secret named 'BOT_TOKEN' or 'bot_token'")
        exit(1)
    print("✅ Bot token found in environment variables")
    
    # Check role IDs
    admin_role_env = os.getenv('ADMIN_ROLE_ID')
    buyer_role_env = os.getenv('BUYER_ROLE_ID')
    
    if admin_role_env:
        print(f"✅ Admin role ID found in environment: {ADMIN_ROLE_ID}")
    else:
        print(f"⚠️ Using default admin role ID: {ADMIN_ROLE_ID}")
        print("💡 Set ADMIN_ROLE_ID environment variable to customize")
    
    if buyer_role_env:
        print(f"✅ Buyer role ID found in environment: {BUYER_ROLE_ID}")
    else:
        print(f"⚠️ Using default buyer role ID: {BUYER_ROLE_ID}")
        print("💡 Set BUYER_ROLE_ID environment variable to customize")
    
    print("🚀 Starting Discord bot...")
    
    try:
        bot.run(bot_token)
    except Exception as e:
        print(f"❌ Failed to start Discord bot: {e}")
        print("Please check your bot token and internet connection")
        exit(1)
