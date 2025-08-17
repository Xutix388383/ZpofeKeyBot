
# Script Marketplace

A complete script marketplace with Flask web interface and Discord bot integration.

## Setup Instructions

### 1. Flask Web Application

The Flask app provides an admin panel where you can manage scripts and view orders.

**Admin Credentials:**
- Username: `Zpofe0902`
- Password: `0902`

**To run the Flask app:**
```bash
python main.py
```

Visit `http://localhost:5000` to access the marketplace.
Visit `http://localhost:5000/admin` to access the admin panel.

### 2. Discord Bot Setup

The Discord bot provides a shop command that creates an interactive panel for users to browse and purchase scripts.

**Setup Steps:**

1. **Create a Discord Application:**
   - Go to https://discord.com/developers/applications
   - Create a new application
   - Go to the "Bot" section and create a bot
   - Copy the bot token

2. **Configure the Bot:**
   - Open `bot.py`
   - Replace `'YOUR_BOT_TOKEN'` with your actual bot token
   - Replace `'YOUR_USER_ID'` with your Discord user ID (for purchase notifications)
   - Update `MARKETPLACE_URL` when you deploy your Flask app

3. **Invite Bot to Server:**
   - Go to OAuth2 > URL Generator in Discord Developer Portal
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Use Slash Commands`, `Embed Links`
   - Use the generated URL to invite the bot

4. **Run the Bot:**
   ```bash
   python bot.py
   ```

### 3. Bot Commands

- `!shop` - Display the interactive script marketplace panel
- `!scripts` - List all available scripts
- `!help_shop` - Show help for shop commands

### 4. Features

**Flask Web Interface:**
- Professional admin panel
- Add/manage scripts
- View orders and statistics
- Secure login system

**Discord Bot:**
- Interactive shop panel with buttons
- Purchase modal forms
- Automatic order processing
- Professional embeds and UI

**Script Management:**
- Categories and pricing
- Feature lists
- Demo links
- Order tracking

### 5. Deployment

Deploy both the Flask app and Discord bot on Replit or your preferred hosting platform. Make sure to update the `MARKETPLACE_URL` in the bot code to point to your deployed Flask application.
