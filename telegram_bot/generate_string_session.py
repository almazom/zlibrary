#!/usr/bin/env python3
"""
Generate String Session - One-Time Authentication
This creates a persistent string session that eliminates file corruption
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def generate_string_session():
    """Generate a stable string session for persistent authentication"""
    
    # Your API credentials
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print("🔐 GENERATING STABLE STRING SESSION")
    print("=" * 50)
    print("This is a ONE-TIME process. The generated string session")
    print("can be used forever without re-authentication.")
    print("=" * 50)
    
    try:
        # Create client with empty string session for first-time auth
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            
            # Get user info
            me = await client.get_me()
            print(f"\n✅ Successfully authenticated!")
            print(f"👤 User: {me.first_name} {me.last_name or ''}")
            print(f"🆔 ID: {me.id}")
            print(f"📞 Phone: {me.phone}")
            
            # Generate string session
            string_session = client.session.save()
            
            print(f"\n🎯 SUCCESS! String session generated:")
            print("=" * 60)
            print(f"{string_session}")
            print("=" * 60)
            
            print(f"\n💾 IMPORTANT: Save this string session!")
            print("- Copy the string above")
            print("- Use it in future scripts to avoid re-authentication")
            print("- Keep it secure - it provides full access to your account")
            
            # Save to file for convenience
            with open('stable_string_session.txt', 'w') as f:
                f.write(string_session)
            print(f"\n📁 Also saved to: stable_string_session.txt")
            
            return string_session
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return None

if __name__ == '__main__':
    result = asyncio.run(generate_string_session())
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print("You can now use this string session for stable book searches")
        print("without the 30-minute re-authentication problem!")
    else:
        print(f"\n❌ FAILED!")
        print("Please check your phone number and SMS code")