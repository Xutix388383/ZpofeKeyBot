
# Discord Script Marketplace Bot

A complete Discord bot-based script marketplace with admin panel and user management.

## Setup Instructions

### 1. Discord Bot Setup

The Discord bot provides two main slash commands:
- `/shop` - Interactive marketplace for users to browse and purchase scripts
- `/admin` - Complete admin panel for marketplace management (admin only)

**Setup Steps:**

1. **Create a Discord Application:**
   - Go to https://discord.com/developers/applications
   - Create a new application
   - Go to the "Bot" section and create a bot
   - Copy the bot token

2. **Configure the Bot:**
   - Add your bot token as a secret named `BOT_TOKEN` or `bot_token`
   - Update `ADMIN_ROLE_ID` and `BUYER_ROLE_ID` in the code with your server's role IDs

3. **Invite Bot to Server:**
   - Go to OAuth2 > URL Generator in Discord Developer Portal
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Use Slash Commands`, `Embed Links`, `Manage Roles`
   - Use the generated URL to invite the bot

4. **Run the Bot:**
   ```bash
   python marketplace_bot.py
   ```

### 2. Bot Commands

**User Commands:**
- `/shop` - Display the interactive script marketplace panel
- `/get_scripts` - Access purchased scripts (requires Buyer role)

**Admin Commands:**
- `/admin` - Access the complete admin control panel

### 3. Admin Panel Features

The `/admin` command provides a comprehensive management interface:

**Script Management:**
- Add new scripts with pricing and categories
- Edit existing scripts (name, price, description)
- Delete scripts from the marketplace
- View all scripts with details

**User Management:**
- Assign scripts to specific users
- View user script assignments
- Remove scripts from users
- Give buyer role to users manually

**Ticket Management:**
- View all payment verification tickets
- Verify payments and assign buyer roles
- Track ticket status and history

**Order Management:**
- View all customer orders
- Track order status and revenue
- Monitor purchase history

### 4. Features

**Interactive Shop:**
- Paginated script browsing
- Shopping cart system
- Add/remove items from cart
- Secure checkout process

**Admin Panel:**
- Role-based access control
- Complete marketplace management
- User script assignment system
- Payment verification workflow

**Security:**
- Admin-only access to management functions
- Role-based permissions
- Secure user verification

### 5. Role Configuration

Make sure to create these roles in your Discord server:
- **Admin Role** - For marketplace administrators
- **Buyer Role** - For verified customers who can access purchased scripts

Update the role IDs in the code:
```python
ADMIN_ROLE_ID = YOUR_ADMIN_ROLE_ID
BUYER_ROLE_ID = YOUR_BUYER_ROLE_ID
```

### 6. Data Storage

The bot uses JSON files for data storage:
- `scripts.json` - Script inventory
- `orders.json` - Customer orders
- `tickets.json` - Payment verification tickets
- `user_scripts.json` - User script assignments

### 7. Deployment

Deploy the bot on Replit or your preferred hosting platform. The bot will automatically create necessary data files on first run.
