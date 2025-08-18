
#!/usr/bin/env python3
"""
Discord Script Marketplace Bot
Main entry point - runs the Discord bot only
"""

import os
import sys

def main():
    """Main entry point"""
    print("🚀 Starting Discord Script Marketplace Bot...")
    
    # Check if marketplace_bot exists
    if not os.path.exists('marketplace_bot.py'):
        print("❌ marketplace_bot.py not found!")
        sys.exit(1)
    
    # Import and run the Discord bot
    try:
        import marketplace_bot
        print("✅ Discord bot module loaded successfully")
    except ImportError as e:
        print(f"❌ Failed to import marketplace_bot: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Discord bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
