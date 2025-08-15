#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib

async def test_account():
    # Load the active account
    config_path = Path("./accounts_config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    for account in config.get('accounts', []):
        if account.get('is_active', False):
            email = account['email']
            password = account['password']
            
            print(f"Testing account: {email}")
            print(f"Password: {password[:5]}...")
            
            try:
                client = AsyncZlib()
                print("Created AsyncZlib client")
                
                # Check if client has expected attributes
                print(f"Client mirror: {getattr(client, 'mirror', 'None')}")
                print(f"Client cookies: {getattr(client, 'cookies', 'None')}")
                
                print("Attempting login...")
                profile = await client.login(email, password)
                print("✅ Login successful!")
                print(f"Profile: {profile}")
                
                limits = await profile.get_limits()
                print(f"Daily remaining: {limits.get('daily_remaining', 0)}")
                
                await client.logout()
                print("✅ Logout successful")
                return True
                
            except Exception as e:
                import traceback
                print(f"❌ Login failed: {e}")
                print(f"Error type: {type(e)}")
                print("Full traceback:")
                traceback.print_exc()
                return False

if __name__ == "__main__":
    asyncio.run(test_account())