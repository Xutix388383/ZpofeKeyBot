
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

# Role IDs
ADMIN_ROLE_ID = 1399949855799119952
BUYER_ROLE_ID = 1406653314589786204

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

@bot.tree.command(name='shop', description='Open the script marketplace shop')
async def shop(interaction: discord.Interaction):
    """Display the shop panel with cart system"""
    scripts = load_scripts()
    
    if not scripts:
        embed = discord.Embed(
            title="🛒 Script Shop",
            description="No scripts available at the moment.\nUse `/edit` to add some scripts!",
            color=0x667eea
        )
        await interaction.response.send_message(embed=embed)
        return
    
    # Create shop embed
    embed = discord.Embed(
        title="🛒 Zpofe's Script Shop",
        description="Premium scripts for your projects. Browse, add to cart, and purchase!",
        color=0x667eea,
        timestamp=datetime.now()
    )
    
    embed.set_footer(text="🛍️ Shop Panel | Use buttons to interact", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    
    # Add cart status
    embed.add_field(
        name="🛒 Your Cart",
        value="Empty - Start adding scripts!",
        inline=False
    )
    
    # Create shop view with cart
    view = ShopView(scripts, [])
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name='get_scripts', description='Get your purchased scripts (Buyer role required)')
async def get_scripts(interaction: discord.Interaction):
    """Allow buyers to get their purchased scripts"""
    if not has_buyer_role(interaction.user):
        await interaction.response.send_message("❌ You need the Buyer role to access this command!", ephemeral=True)
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

@bot.tree.command(name='edit', description='Full marketplace content editor (Admin only)')
async def edit_marketplace(interaction: discord.Interaction):
    """Complete marketplace content editor - admin only"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You need administrator permissions to edit the marketplace!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🛠️ Marketplace Content Editor",
        description="Full control panel for managing your marketplace:",
        color=0xffa500
    )
    
    embed.add_field(
        name="📝 Content Management",
        value="Add, edit, or remove scripts\nManage categories and pricing\nUpdate descriptions and features",
        inline=True
    )
    
    embed.add_field(
        name="🎨 Shop Customization",
        value="Edit shop title and branding\nCustomize embed colors\nModify shop descriptions",
        inline=True
    )
    
    embed.add_field(
        name="📊 Analytics & Orders",
        value="View sales analytics\nManage customer orders\nTrack popular scripts",
        inline=True
    )
    
    embed.add_field(
        name="🎫 Ticket Management",
        value="View and manage tickets\nVerify payments\nAssign scripts to users",
        inline=True
    )
    
    embed.add_field(
        name="👥 User Management",
        value="Assign buyer roles\nManage user scripts\nView user purchases",
        inline=True
    )
    
    embed.set_footer(text="Admin Content Editor | Full Marketplace Control")
    
    view = AdminEditView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name='verify_payment', description='Verify payment and give buyer role (Admin only)')
async def verify_payment(interaction: discord.Interaction, user: discord.Member, ticket_id: int):
    """Admin command to verify payment and assign buyer role"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
        return
    
    tickets = load_tickets()
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    
    if not ticket:
        await interaction.response.send_message(f"❌ Ticket #{ticket_id} not found!", ephemeral=True)
        return
    
    if ticket['status'] == 'verified':
        await interaction.response.send_message(f"❌ Ticket #{ticket_id} is already verified!", ephemeral=True)
        return
    
    # Give buyer role
    buyer_role = interaction.guild.get_role(BUYER_ROLE_ID)
    if buyer_role and buyer_role not in user.roles:
        await user.add_roles(buyer_role)
    
    # Update ticket status
    ticket['status'] = 'verified'
    ticket['verified_by'] = interaction.user.id
    ticket['verified_at'] = datetime.now().isoformat()
    save_tickets(tickets)
    
    embed = discord.Embed(
        title="✅ Payment Verified",
        description=f"Payment for ticket #{ticket_id} has been verified!",
        color=0x28a745
    )
    
    embed.add_field(
        name="👤 User",
        value=f"{user.mention} ({user.id})",
        inline=True
    )
    
    embed.add_field(
        name="🎫 Ticket",
        value=f"ID: #{ticket_id}\nStatus: Verified",
        inline=True
    )
    
    embed.add_field(
        name="🏷️ Role Assigned",
        value="Buyer role has been given to the user",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)
    
    # Notify user
    try:
        user_embed = discord.Embed(
            title="✅ Payment Verified!",
            description="Your payment has been verified and you've been given the Buyer role!",
            color=0x28a745
        )
        user_embed.add_field(
            name="📦 Next Steps",
            value="You can now use `/get_scripts` to access your purchased scripts!",
            inline=False
        )
        await user.send(embed=user_embed)
    except:
        pass

@bot.tree.command(name='assign_script', description='Assign a script to a user (Admin only)')
async def assign_script(interaction: discord.Interaction, user: discord.Member, script_id: int):
    """Admin command to assign scripts to users"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
        return
    
    scripts = load_scripts()
    script = next((s for s in scripts if s['id'] == script_id), None)
    
    if not script:
        await interaction.response.send_message(f"❌ Script with ID {script_id} not found!", ephemeral=True)
        return
    
    user_scripts = load_user_scripts()
    user_id = str(user.id)
    
    if user_id not in user_scripts:
        user_scripts[user_id] = []
    
    if script_id in user_scripts[user_id]:
        await interaction.response.send_message(f"❌ User already has access to script: {script['name']}", ephemeral=True)
        return
    
    user_scripts[user_id].append(script_id)
    save_user_scripts(user_scripts)
    
    embed = discord.Embed(
        title="✅ Script Assigned",
        description=f"Script has been assigned to {user.mention}!",
        color=0x28a745
    )
    
    embed.add_field(
        name="📄 Script Details",
        value=f"**Name:** {script['name']}\n**ID:** {script_id}\n**Category:** {script['category']}",
        inline=False
    )
    
    embed.add_field(
        name="👤 Assigned To",
        value=f"{user.mention} ({user.id})",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)
    
    # Notify user
    try:
        user_embed = discord.Embed(
            title="📦 New Script Available!",
            description=f"You've been given access to: **{script['name']}**",
            color=0x28a745
        )
        user_embed.add_field(
            name="📥 How to Access",
            value="Use `/get_scripts` to download your script!",
            inline=False
        )
        await user.send(embed=user_embed)
    except:
        pass

@bot.tree.command(name='tickets', description='View and manage tickets (Admin only)')
async def view_tickets(interaction: discord.Interaction):
    """Admin command to view all tickets"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
        return
    
    tickets = load_tickets()
    
    if not tickets:
        embed = discord.Embed(
            title="🎫 No Tickets",
            description="No tickets found.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎫 Ticket Management",
        description=f"Total tickets: {len(tickets)}",
        color=0x667eea
    )
    
    # Show recent tickets
    recent_tickets = sorted(tickets, key=lambda x: x['created_at'], reverse=True)[:10]
    
    for ticket in recent_tickets:
        status_emoji = "✅" if ticket['status'] == 'verified' else "⏳"
        embed.add_field(
            name=f"{status_emoji} Ticket #{ticket['id']}",
            value=f"**User:** <@{ticket['user_id']}>\n**Order:** #{ticket['order_id']}\n**Status:** {ticket['status'].title()}\n**Created:** {ticket['created_at'][:10]}",
            inline=True
        )
    
    if len(tickets) > 10:
        embed.set_footer(text=f"Showing 10 most recent tickets of {len(tickets)} total")
    
    view = TicketManagementView(tickets)
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

class TicketManagementView(discord.ui.View):
    def __init__(self, tickets):
        super().__init__(timeout=600)
        self.tickets = tickets
    
    @discord.ui.button(label="📊 Ticket Stats", style=discord.ButtonStyle.primary, emoji="📈")
    async def ticket_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        pending_tickets = len([t for t in self.tickets if t['status'] == 'pending'])
        verified_tickets = len([t for t in self.tickets if t['status'] == 'verified'])
        
        embed = discord.Embed(
            title="📊 Ticket Statistics",
            description="Overview of all tickets:",
            color=0x667eea
        )
        
        embed.add_field(
            name="📈 Summary",
            value=f"**Total Tickets:** {len(self.tickets)}\n**Pending:** {pending_tickets}\n**Verified:** {verified_tickets}",
            inline=True
        )
        
        embed.add_field(
            name="⏳ Pending Tickets",
            value=f"{pending_tickets} tickets awaiting verification",
            inline=True
        )
        
        embed.add_field(
            name="✅ Completion Rate",
            value=f"{(verified_tickets/len(self.tickets)*100):.1f}%" if self.tickets else "0%",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self, scripts, cart):
        super().__init__(timeout=600)
        self.scripts = scripts
        self.cart = cart
        self.current_page = 0
        self.scripts_per_page = 5
        
        self.update_buttons()
    
    def update_buttons(self):
        self.clear_items()
        
        total_pages = (len(self.scripts) + self.scripts_per_page - 1) // self.scripts_per_page
        start_idx = self.current_page * self.scripts_per_page
        end_idx = min(start_idx + self.scripts_per_page, len(self.scripts))
        current_scripts = self.scripts[start_idx:end_idx]
        
        for script in current_scripts:
            button = ScriptShopButton(script, script in [s['id'] for s in self.cart])
            self.add_item(button)
        
        if total_pages > 1:
            prev_button = discord.ui.Button(
                label="◀️ Previous",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page == 0
            )
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
            
            next_button = discord.ui.Button(
                label="▶️ Next",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page >= total_pages - 1
            )
            next_button.callback = self.next_page
            self.add_item(next_button)
        
        cart_button = discord.ui.Button(
            label=f"🛒 View Cart ({len(self.cart)})",
            style=discord.ButtonStyle.primary,
            emoji="🛒"
        )
        cart_button.callback = self.view_cart
        self.add_item(cart_button)
        
        if self.cart:
            checkout_button = discord.ui.Button(
                label="💳 Checkout",
                style=discord.ButtonStyle.success,
                emoji="💰"
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
            title="🛒 Zpofe's Script Shop",
            description="Premium scripts for your projects. Browse, add to cart, and purchase!",
            color=0x667eea,
            timestamp=datetime.now()
        )
        
        for script in current_scripts:
            in_cart = "🛒 " if script['id'] in [s['id'] for s in self.cart] else ""
            embed.add_field(
                name=f"{in_cart}{script['name']}",
                value=f"💰 **Price:** ${script['price']:.2f}\n📁 **Category:** {script['category']}",
                inline=True
            )
        
        if self.cart:
            total_price = sum(item['price'] for item in self.cart)
            cart_items = ", ".join([item['name'] for item in self.cart])
            embed.add_field(
                name="🛒 Your Cart",
                value=f"**Items:** {cart_items}\n**Total:** ${total_price:.2f}",
                inline=False
            )
        else:
            embed.add_field(
                name="🛒 Your Cart",
                value="Empty - Start adding scripts!",
                inline=False
            )
        
        embed.set_footer(text=f"🛍️ Page {self.current_page + 1}/{(len(self.scripts) + self.scripts_per_page - 1) // self.scripts_per_page} | Shop Panel")
        
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
    
    async def checkout(self, interaction: discord.Interaction):
        if not self.cart:
            await interaction.response.send_message("🛒 Your cart is empty!", ephemeral=True)
            return
        
        modal = CheckoutModal(self.cart)
        await interaction.response.send_modal(modal)

class ScriptShopButton(discord.ui.Button):
    def __init__(self, script, in_cart=False):
        self.script = script
        
        if in_cart:
            label = f"Remove from Cart"
            style = discord.ButtonStyle.danger
            emoji = "🗑️"
        else:
            label = f"Add to Cart"
            style = discord.ButtonStyle.success
            emoji = "🛒"
        
        super().__init__(
            label=label,
            style=style,
            emoji=emoji
        )
    
    async def callback(self, interaction: discord.Interaction):
        shop_view = self.view
        
        script_in_cart = any(item['id'] == self.script['id'] for item in shop_view.cart)
        
        if script_in_cart:
            shop_view.cart = [item for item in shop_view.cart if item['id'] != self.script['id']]
        else:
            shop_view.cart.append(self.script)
        
        shop_view.update_buttons()
        await shop_view.update_shop_embed(interaction)

class CartView(discord.ui.View):
    def __init__(self, cart, shop_view):
        super().__init__(timeout=300)
        self.cart = cart
        self.shop_view = shop_view
    
    @discord.ui.button(label="🗑️ Clear Cart", style=discord.ButtonStyle.danger)
    async def clear_cart(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.shop_view.cart.clear()
        embed = discord.Embed(
            title="🛒 Cart Cleared",
            description="Your cart has been cleared!",
            color=0xff0000
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="💳 Proceed to Checkout", style=discord.ButtonStyle.success)
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
            value="1. Send payment for your order\n2. Take a screenshot of your payment confirmation\n3. A private ticket channel will be created for you\n4. Upload your payment proof in the ticket\n5. Wait for staff verification\n6. Once verified, you'll get the Buyer role and access to your scripts!",
            inline=False
        )
        
        embed.set_footer(text="Thank you for your purchase! | ScriptHub")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Create private ticket channel
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        
        if not category:
            category = await guild.create_category("Tickets")
        
        # Set permissions for the ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
        }
        
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{ticket['id']}-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )
        
        # Send initial message in ticket channel
        ticket_embed = discord.Embed(
            title=f"🎫 Payment Verification Ticket #{ticket['id']}",
            description="Please upload your payment confirmation screenshot here.",
            color=0x667eea
        )
        
        ticket_embed.add_field(
            name="📋 Order Information",
            value=f"**Order ID:** #{order['id']}\n**Total Amount:** ${total_price:.2f}\n**Customer:** {interaction.user.mention}",
            inline=False
        )
        
        ticket_embed.add_field(
            name="📸 Instructions",
            value="1. Upload a clear screenshot of your payment confirmation\n2. Wait for staff to verify your payment\n3. Once verified, you'll receive the Buyer role and script access",
            inline=False
        )
        
        await ticket_channel.send(embed=ticket_embed)
        await ticket_channel.send(f"{interaction.user.mention} - Your payment verification ticket has been created!")

class AdminEditView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
    
    @discord.ui.button(label="➕ Add Script", style=discord.ButtonStyle.success, emoji="📝")
    async def add_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddScriptModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Manage Scripts", style=discord.ButtonStyle.primary, emoji="📚")
    async def manage_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        scripts = load_scripts()
        
        if not scripts:
            embed = discord.Embed(
                title="📋 No Scripts",
                description="No scripts found. Add some with the 'Add Script' button!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 Script Management Center",
            description="Manage all your marketplace scripts:",
            color=0x667eea
        )
        
        for script in scripts[:8]:
            embed.add_field(
                name=f"ID: {script['id']} - {script['name']}",
                value=f"**Price:** ${script['price']:.2f}\n**Category:** {script['category']}\n**Status:** Active",
                inline=True
            )
        
        if len(scripts) > 8:
            embed.add_field(
                name="📊 Total Scripts",
                value=f"{len(scripts)} scripts in marketplace\nShowing first 8 scripts",
                inline=False
            )
        
        view = AdvancedScriptManagementView(scripts)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🎫 Ticket Management", style=discord.ButtonStyle.secondary, emoji="🎟️")
    async def ticket_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        await view_tickets(interaction)
    
    @discord.ui.button(label="👥 User Management", style=discord.ButtonStyle.secondary, emoji="👤")
    async def user_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_scripts = load_user_scripts()
        
        embed = discord.Embed(
            title="👥 User Management",
            description="Manage user scripts and roles:",
            color=0x9f7aea
        )
        
        total_users = len(user_scripts)
        total_assignments = sum(len(scripts) for scripts in user_scripts.values())
        
        embed.add_field(
            name="📊 Statistics",
            value=f"**Users with Scripts:** {total_users}\n**Total Script Assignments:** {total_assignments}",
            inline=False
        )
        
        # Show recent assignments
        if user_scripts:
            recent_text = ""
            for user_id, script_ids in list(user_scripts.items())[:5]:
                recent_text += f"<@{user_id}>: {len(script_ids)} scripts\n"
            
            embed.add_field(
                name="👤 Recent Users",
                value=recent_text or "No users with scripts",
                inline=False
            )
        
        view = UserManagementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class UserManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📋 View User Scripts", style=discord.ButtonStyle.primary, emoji="👥")
    async def view_user_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ViewUserScriptsModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Remove User Scripts", style=discord.ButtonStyle.danger, emoji="❌")
    async def remove_user_scripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RemoveUserScriptsModal()
        await interaction.response.send_modal(modal)

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

class AdvancedScriptManagementView(discord.ui.View):
    def __init__(self, scripts):
        super().__init__(timeout=300)
        self.scripts = scripts
    
    @discord.ui.button(label="✏️ Edit Script", style=discord.ButtonStyle.primary, emoji="📝")
    async def edit_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EditScriptModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Delete Script", style=discord.ButtonStyle.danger, emoji="❌")
    async def delete_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DeleteScriptModal()
        await interaction.response.send_modal(modal)

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
            placeholder="e.g., Gaming, Automation, Web",
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
        script_to_edit = None
        
        for script in scripts:
            if script['id'] == script_id:
                script_to_edit = script
                break
        
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

# Run the bot
if __name__ == "__main__":
    print("Starting Discord Script Shop Bot...")
    
    bot_token = os.getenv('BOT_TOKEN') or os.getenv('bot_token')
    
    if not bot_token:
        print("❌ Bot token environment variable not found!")
        print("Please add your Discord bot token as a secret named 'BOT_TOKEN' or 'bot_token'")
        exit(1)
    
    print("✅ Bot token found in environment variables")
    bot.run(bot_token)
