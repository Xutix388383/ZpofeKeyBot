
import discord
from discord.ext import commands
import json
import requests
from datetime import datetime
import socket
import os

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Marketplace URL with fallback ports
POSSIBLE_PORTS = [5000, 8080, 3000, 8000, 9000, 7000, 6000, 4000]
MARKETPLACE_URL = None

def find_marketplace_url():
    """Find the active marketplace server URL"""
    global MARKETPLACE_URL
    
    for port in POSSIBLE_PORTS:
        try:
            test_url = f"http://localhost:{port}"
            response = requests.get(test_url, timeout=2)
            if response.status_code == 200:
                MARKETPLACE_URL = test_url
                print(f"✅ Found marketplace server at: {MARKETPLACE_URL}")
                return MARKETPLACE_URL
        except requests.exceptions.RequestException:
            continue
    
    print("⚠️ No marketplace server found. Using fallback URL.")
    MARKETPLACE_URL = "http://localhost:5000"  # Default fallback
    return MARKETPLACE_URL

def load_scripts():
    """Load scripts from the marketplace with error handling"""
    try:
        with open('scripts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ scripts.json not found, creating empty list")
        return []
    except json.JSONDecodeError:
        print("❌ Error reading scripts.json, using empty list")
        return []
    except Exception as e:
        print(f"❌ Unexpected error loading scripts: {e}")
        return []

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    find_marketplace_url()
    print(f"🔗 Marketplace URL set to: {MARKETPLACE_URL}")

@bot.command(name='shop')
async def shop_panel(ctx):
    """Display the script marketplace panel with error handling"""
    try:
        scripts = load_scripts()
        
        if not scripts:
            embed = discord.Embed(
                title="🛒 Script Marketplace",
                description="No scripts available at the moment.\nContact an admin to add scripts!",
                color=0x667eea
            )
            await ctx.send(embed=embed)
            return
        
        # Create main shop embed
        embed = discord.Embed(
            title="🛒 Zpofe's Script Marketplace",
            description="Premium scripts for your projects. Click the buttons below to purchase!",
            color=0x667eea,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="ScriptHub Marketplace", icon_url=bot.user.avatar.url if bot.user.avatar else None)
        
        # Add scripts to embed (limit to 5 for readability)
        for i, script in enumerate(scripts[:5]):
            embed.add_field(
                name=f"{script['name']} - ${script['price']:.2f}",
                value=f"**Category:** {script['category']}\n**Description:** {script['description'][:100]}{'...' if len(script['description']) > 100 else ''}",
                inline=False
            )
        
        if len(scripts) > 5:
            embed.add_field(
                name="📝 More Scripts Available",
                value=f"And {len(scripts) - 5} more scripts! Use the buttons below to browse all.",
                inline=False
            )
        
        # Create view with buttons
        view = ShopView(scripts)
        await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        print(f"❌ Error in shop command: {e}")
        error_embed = discord.Embed(
            title="❌ Shop Error",
            description="There was an error loading the shop. Please try again later.",
            color=0xff0000
        )
        await ctx.send(embed=error_embed)

class ShopView(discord.ui.View):
    def __init__(self, scripts):
        super().__init__(timeout=300)
        self.scripts = scripts
        
        # Add script buttons (Discord limits to 25 components per view)
        for i, script in enumerate(scripts[:20]):  # Limit to 20 scripts
            button = ScriptButton(script, i)
            self.add_item(button)
    
    async def on_timeout(self):
        # Disable all buttons when view times out
        for item in self.children:
            item.disabled = True

class ScriptButton(discord.ui.Button):
    def __init__(self, script, index):
        self.script = script
        emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", 
                     "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫", "⚪", "🔸"]
        
        super().__init__(
            label=f"{script['name']} - ${script['price']:.2f}",
            style=discord.ButtonStyle.primary,
            emoji=emoji_list[index % len(emoji_list)] if index < len(emoji_list) else "💎"
        )
    
    async def callback(self, interaction: discord.Interaction):
        try:
            # Create purchase embed
            embed = discord.Embed(
                title=f"💰 Purchase: {self.script['name']}",
                description=f"**Price:** ${self.script['price']:.2f}\n**Category:** {self.script['category']}",
                color=0x28a745
            )
            
            embed.add_field(
                name="📝 Description",
                value=self.script['description'],
                inline=False
            )
            
            if self.script.get('features'):
                features_text = "\n".join([f"✅ {feature}" for feature in self.script['features'][:5]])
                embed.add_field(
                    name="🌟 Features",
                    value=features_text,
                    inline=False
                )
            
            embed.add_field(
                name="📞 How to Purchase",
                value="Fill out the purchase form below to complete your order!",
                inline=False
            )
            
            embed.set_footer(text=f"Script ID: {self.script['id']} | ScriptHub Marketplace")
            
            # Create purchase view
            purchase_view = PurchaseView(self.script)
            
            await interaction.response.send_message(embed=embed, view=purchase_view, ephemeral=True)
            
        except Exception as e:
            print(f"❌ Error in script button callback: {e}")
            error_embed = discord.Embed(
                title="❌ Button Error",
                description="There was an error processing your request. Please try again.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

class PurchaseView(discord.ui.View):
    def __init__(self, script):
        super().__init__(timeout=300)
        self.script = script
    
    @discord.ui.button(label="💳 Purchase Now", style=discord.ButtonStyle.success, emoji="💰")
    async def purchase_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            modal = PurchaseModal(self.script)
            await interaction.response.send_modal(modal)
        except Exception as e:
            print(f"❌ Error opening purchase modal: {e}")
            error_embed = discord.Embed(
                title="❌ Purchase Error",
                description="There was an error opening the purchase form. Please try again.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Purchase Cancelled",
            description="Feel free to browse other scripts!",
            color=0xff0000
        )
        await interaction.response.edit_message(embed=embed, view=None)

class PurchaseModal(discord.ui.Modal):
    def __init__(self, script):
        super().__init__(title=f"Purchase: {script['name']}")
        self.script = script
        
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
        try:
            # Create order data
            order_data = {
                'email': self.email.value,
                'discord': self.discord_user.value
            }
            
            # Find active marketplace URL
            if not MARKETPLACE_URL:
                find_marketplace_url()
            
            # Try multiple URLs in case of port changes
            success = False
            last_error = None
            
            for port in POSSIBLE_PORTS:
                try:
                    url = f"http://localhost:{port}/purchase/{self.script['id']}"
                    response = requests.post(url, data=order_data, timeout=5)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        embed = discord.Embed(
                            title="✅ Order Placed Successfully!",
                            description=f"Your order for **{self.script['name']}** has been placed!",
                            color=0x28a745
                        )
                        
                        embed.add_field(
                            name="📧 Order Details",
                            value=f"**Order ID:** #{result.get('order_id', 'N/A')}\n**Script:** {self.script['name']}\n**Price:** ${self.script['price']:.2f}\n**Email:** {self.email.value}",
                            inline=False
                        )
                        
                        embed.add_field(
                            name="📞 Next Steps",
                            value="You will be contacted shortly with payment instructions and script delivery details.",
                            inline=False
                        )
                        
                        embed.set_footer(text="Thank you for your purchase! | ScriptHub")
                        success = True
                        break
                        
                except requests.exceptions.RequestException as e:
                    last_error = e
                    continue
            
            if not success:
                # Fallback: save order locally
                try:
                    orders = []
                    try:
                        with open('orders.json', 'r') as f:
                            orders = json.load(f)
                    except FileNotFoundError:
                        pass
                    
                    order = {
                        'id': len(orders) + 1,
                        'script_id': self.script['id'],
                        'script_name': self.script['name'],
                        'buyer_email': self.email.value,
                        'buyer_discord': self.discord_user.value,
                        'price': self.script['price'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat()
                    }
                    
                    orders.append(order)
                    with open('orders.json', 'w') as f:
                        json.dump(orders, f, indent=2)
                    
                    embed = discord.Embed(
                        title="✅ Order Saved Locally!",
                        description=f"Your order for **{self.script['name']}** has been saved!",
                        color=0x28a745
                    )
                    
                    embed.add_field(
                        name="📧 Order Details",
                        value=f"**Order ID:** #{order['id']}\n**Script:** {self.script['name']}\n**Price:** ${self.script['price']:.2f}\n**Email:** {self.email.value}",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📞 Next Steps",
                        value="Your order has been saved locally. Contact an admin to complete the purchase.",
                        inline=False
                    )
                    
                except Exception as save_error:
                    print(f"❌ Error saving order locally: {save_error}")
                    embed = discord.Embed(
                        title="❌ Order Failed",
                        description=f"There was an error processing your order: {last_error}\n\nPlease contact support directly.",
                        color=0xff0000
                    )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"❌ Error in purchase modal submit: {e}")
            error_embed = discord.Embed(
                title="❌ Purchase Error",
                description="There was an error processing your purchase. Please try again or contact support.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

# Additional commands with error handling
@bot.command(name='scripts')
async def list_scripts(ctx):
    """List all available scripts with error handling"""
    try:
        scripts = load_scripts()
        
        if not scripts:
            await ctx.send("No scripts available.")
            return
        
        embed = discord.Embed(
            title="📜 Available Scripts",
            description="Here are all available scripts:",
            color=0x667eea
        )
        
        for script in scripts:
            embed.add_field(
                name=f"{script['name']} - ${script['price']:.2f}",
                value=f"Category: {script['category']}\nID: {script['id']}",
                inline=True
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"❌ Error in scripts command: {e}")
        error_embed = discord.Embed(
            title="❌ Scripts Error",
            description="There was an error loading the scripts list.",
            color=0xff0000
        )
        await ctx.send(embed=error_embed)

@bot.command(name='help_shop')
async def help_shop(ctx):
    """Show help for shop commands"""
    try:
        embed = discord.Embed(
            title="🛠️ Shop Commands Help",
            description="Available commands for the script marketplace:",
            color=0x667eea
        )
        
        embed.add_field(
            name="!shop",
            value="Display the interactive script marketplace panel",
            inline=False
        )
        
        embed.add_field(
            name="!scripts",
            value="List all available scripts",
            inline=False
        )
        
        embed.add_field(
            name="!help_shop",
            value="Show this help message",
            inline=False
        )
        
        embed.add_field(
            name="🌐 Web Interface",
            value=f"Access the web interface at: {MARKETPLACE_URL or 'http://localhost:5000'}",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"❌ Error in help command: {e}")
        await ctx.send("❌ Error displaying help. Please try again.")

# Global error handler
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Discord bot error in {event}: {args}")

# Run the bot
if __name__ == "__main__":
    print("Starting Discord bot with multi-port support...")
    print("🔍 Bot will automatically detect marketplace server on available ports")
    print("📱 Supported ports:", POSSIBLE_PORTS)
    
    # Get bot token from environment variables
    bot_token = os.getenv('BOT_TOKEN') or os.getenv('bot_token')
    
    if not bot_token:
        print("❌ Bot token environment variable not found!")
        print("Please add your Discord bot token as a secret named 'BOT_TOKEN' or 'bot_token'")
        exit(1)
    
    print("✅ Bot token found in environment variables")
    
    try:
        bot.run(bot_token)
    except Exception as e:
        print(f"❌ Failed to start Discord bot: {e}")
        print("Please check your bot token and internet connection")
        exit(1)
