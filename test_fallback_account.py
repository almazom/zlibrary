#!/usr/bin/env python3
"""
Test the fallback account that's not in accounts_config.json
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_fallback_account():
    """Test the almazomkz@gmail.com account"""
    
    email = "almazomkz@gmail.com"
    password = "tataronrails78"
    
    print(f"🧪 TESTING FALLBACK ACCOUNT: {email}")
    print(f"{'='*60}")
    
    login_url = "https://z-library.sk/rpc.php"
    
    data = {
        "isModal": True,
        "email": email,
        "password": password,
        "action": "login",
        "redirectUrl": "",
        "gg_json_mode": 1,
    }
    
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            print(f"📡 Sending login request...")
            print(f"👤 Email: {email}")
            
            async with session.post(login_url, data=data) as response:
                print(f"📊 HTTP Status: {response.status}")
                
                text = await response.text()
                print(f"📝 Response length: {len(text)} characters")
                
                if text:
                    try:
                        json_resp = json.loads(text)
                        print(f"📋 Response: {json.dumps(json_resp, indent=2)}")
                        
                        if 'errors' in json_resp and json_resp['errors']:
                            errors = json_resp['errors']
                            for error in errors:
                                code = error.get('code', 'Unknown')
                                message = error.get('message', 'Unknown')
                                
                                if code == 99 and "too many logins" in message.lower():
                                    print(f"🔴 RATE LIMITED: {message}")
                                    return False
                                elif code == 1:
                                    print(f"❌ AUTH FAILED: {message}")
                                    return False
                                else:
                                    print(f"🔍 OTHER ERROR: {message}")
                                    return False
                        
                        elif 'response' in json_resp and json_resp['response'] is not None:
                            print(f"🟢 SUCCESS! Account is working!")
                            return True
                        else:
                            print(f"🔴 FAILED: Null response (likely rate limited)")
                            return False
                            
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON response")
                        return False
                else:
                    print(f"❌ Empty response")
                    return False
                    
        except Exception as e:
            print(f"💥 Error: {e}")
            return False

if __name__ == "__main__":
    result = asyncio.run(test_fallback_account())
    if result:
        print(f"\n🎉 GOOD NEWS: Fallback account is working!")
        print(f"📚 Book search should succeed with this account!")
    else:
        print(f"\n😔 Fallback account is also blocked/failed")
        print(f"⏳ All accounts need to wait for rate limit reset")