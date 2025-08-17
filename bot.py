
import discord
from discord.ext import commands
import json
import requests
from datetime import datetime

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Your Flask app URL (update this when deployed)
MARKETPLACE_URL = "http://localhost:5000"

def load_scripts():
    """Load scripts from the marketplace"""
    try:
        with open('scripts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='shop')
async def shop_panel(ctx):
    """Display the script marketplace panel"""
    scripts = load_scripts()
    
    if not scripts:
        embed = discord.Embed(
            title="🛒 Script Marketplace",
            description="No scripts available at the moment.",
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
            value="Contact <@YOUR_USER_ID> to complete the purchase!\nProvide your Discord username and email address.",
            inline=False
        )
        
        embed.set_footer(text=f"Script ID: {self.script['id']} | ScriptHub Marketplace")
        
        # Create purchase view
        purchase_view = PurchaseView(self.script)
        
        await interaction.response.send_message(embed=embed, view=purchase_view, ephemeral=True)

class PurchaseView(discord.ui.View):
    def __init__(self, script):
        super().__init__(timeout=300)
        self.script = script
    
    @discord.ui.button(label="💳 Purchase Now", style=discord.ButtonStyle.success, emoji="💰")
    async def purchase_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PurchaseModal(self.script)
        await interaction.response.send_modal(modal)
    
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
        # Create order data
        order_data = {
            'email': self.email.value,
            'discord': self.discord_user.value
        }
        
        try:
            # Submit order to Flask app
            response = requests.post(
                f"{MARKETPLACE_URL}/purchase/{self.script['id']}", 
                data=order_data,
                timeout=10
            )
            
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
                
            else:
                embed = discord.Embed(
                    title="❌ Order Failed",
                    description="There was an error processing your order. Please try again or contact support.",
                    color=0xff0000
                )
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Connection Error",
                description="Could not connect to the marketplace. Please try again later.",
                color=0xff0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Additional commands
@bot.command(name='scripts')
async def list_scripts(ctx):
    """List all available scripts"""
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

@bot.command(name='help_shop')
async def help_shop(ctx):
    """Show help for shop commands"""
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
    
    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    print("Starting Discord bot...")
    print("Make sure to:")
    print("1. Replace 'YOUR_BOT_TOKEN' with your actual bot token")
    print("2. Replace 'YOUR_USER_ID' with your Discord user ID")
    print("3. Update MARKETPLACE_URL when you deploy your Flask app")
    
    # Replace with your actual bot token
    bot.run('YOUR_BOT_TOKEN')
