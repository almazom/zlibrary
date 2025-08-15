#!/usr/bin/env python3
import asyncio
import aiohttp
import json

async def test_zlib_api():
    """Test direct connection to Z-Library API"""
    
    # Test basic connectivity
    login_url = "https://z-library.sk/rpc.php"
    
    data = {
        "isModal": True,
        "email": "almazomam2@gmail.com",
        "password": "tataronrails78",
        "action": "login",
        "redirectUrl": "",
        "gg_json_mode": 1,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"Testing POST to: {login_url}")
            print(f"Data: {data}")
            
            async with session.post(login_url, data=data) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                text = await response.text()
                print(f"Response length: {len(text)} chars")
                print(f"First 500 chars: {text[:500]}")
                
                if text:
                    try:
                        json_resp = json.loads(text)
                        print(f"JSON response: {json.dumps(json_resp, indent=2)}")
                    except json.JSONDecodeError:
                        print("Response is not valid JSON")
                else:
                    print("Empty response")
                    
    except Exception as e:
        print(f"Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_zlib_api())