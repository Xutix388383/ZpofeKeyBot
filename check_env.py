
#!/usr/bin/env python3
"""
Environment Variable Checker for Discord Marketplace Bot
Run this script to verify all required environment variables are set correctly.
"""

import os

def check_env_vars():
    print("🔍 Environment Variable Check")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        'BOT_TOKEN': 'Discord bot token (required)',
        'bot_token': 'Alternative Discord bot token name (optional)'
    }
    
    # Optional environment variables with defaults
    optional_vars = {
        'ADMIN_ROLE_ID': '1399949855799119952',
        'BUYER_ROLE_ID': '1406653314589786204', 
        'ADMIN_USERNAME': 'Zpofe0902',
        'ADMIN_PASSWORD': '0902'
    }
    
    all_good = True
    
    print("📋 Required Variables:")
    bot_token_found = False
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * min(len(value), 8)}... ({description})")
            if 'token' in var.lower():
                bot_token_found = True
        else:
            print(f"  ❌ {var}: Not set ({description})")
    
    if not bot_token_found:
        print("  ❌ No bot token found! Set either BOT_TOKEN or bot_token")
        all_good = False
    
    print("\n📝 Optional Variables (with defaults):")
    for var, default in optional_vars.items():
        value = os.getenv(var)
        if value:
            if 'password' in var.lower():
                print(f"  ✅ {var}: {'*' * len(value)} (custom)")
            else:
                print(f"  ✅ {var}: {value} (custom)")
        else:
            print(f"  ⚠️  {var}: {default} (default)")
    
    print("\n📁 Data Files:")
    data_files = ['scripts.json', 'orders.json', 'tickets.json', 'user_scripts.json']
    for file in data_files:
        if os.path.exists(file):
            print(f"  ✅ {file}: Exists")
        else:
            print(f"  ⚠️  {file}: Will be created on first run")
    
    print("\n🔧 Configuration Summary:")
    if all_good:
        print("  ✅ All required environment variables are set!")
        print("  🚀 Your bot should start successfully")
    else:
        print("  ❌ Missing required environment variables")
        print("  💡 Add missing variables using Replit Secrets")
    
    print("\n💡 To add environment variables in Replit:")
    print("  1. Click the 'Secrets' tab in the left sidebar")
    print("  2. Click 'New Secret'")
    print("  3. Add your BOT_TOKEN with your Discord bot token")
    print("  4. Optionally add other variables for customization")
    
    return all_good

if __name__ == "__main__":
    check_env_vars()
