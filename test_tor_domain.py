#!/usr/bin/env python3
"""
Test Z-Library TOR domain to see if it has different rate limits
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_tor_domain():
    """Test the TOR domain for Z-Library"""
    
    # From the source code
    tor_domain = "http://bookszlibb74ugqojhzhg2a63w5i2atv5bqarulgczawnbmsb6s6qead.onion"
    
    print(f"🧅 TESTING TOR DOMAIN")
    print(f"{'='*60}")
    print(f"🌐 Domain: {tor_domain}")
    print(f"⚠️  Note: This requires TOR proxy/connection")
    
    # Test basic connectivity first
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print(f"📡 Testing basic connectivity...")
            
            # Try to connect without proxy first (will likely fail)
            async with session.get(tor_domain) as response:
                print(f"📊 HTTP Status: {response.status}")
                text = await response.text()
                print(f"📝 Response length: {len(text)} characters")
                print(f"✅ TOR domain is accessible without proxy!")
                return True
                
    except asyncio.TimeoutError:
        print(f"⏰ Connection timeout - TOR domain requires TOR proxy")
        return False
    except aiohttp.ClientError as e:
        print(f"🌐 Connection failed: {e}")
        print(f"💡 This is expected - TOR domains require TOR proxy/connection")
        return False
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False

async def test_clearnet_alternatives():
    """Test alternative clearnet domains for Z-Library"""
    
    # Some alternative domains that might work
    alternative_domains = [
        "https://singlelogin.re/",
        "https://z-lib.org/",
        "https://zlibrary-global.se/",
        "https://1lib.sk/"
    ]
    
    print(f"\n🌍 TESTING ALTERNATIVE CLEARNET DOMAINS")
    print(f"{'='*60}")
    
    working_domains = []
    
    for domain in alternative_domains:
        print(f"\n🔍 Testing: {domain}")
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(domain) as response:
                    print(f"  📊 Status: {response.status}")
                    
                    if response.status == 200:
                        text = await response.text()
                        if "z-library" in text.lower() or "zlibrary" in text.lower():
                            print(f"  ✅ Working Z-Library domain!")
                            working_domains.append(domain)
                        else:
                            print(f"  ⚠️  Responds but may not be Z-Library")
                    else:
                        print(f"  ❌ HTTP error: {response.status}")
                        
        except asyncio.TimeoutError:
            print(f"  ⏰ Timeout")
        except aiohttp.ClientError as e:
            print(f"  🌐 Connection failed: {e}")
        except Exception as e:
            print(f"  💥 Error: {e}")
    
    return working_domains

async def main():
    print(f"🔍 Z-Library Alternative Domain Testing")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test TOR domain
    await test_tor_domain()
    
    # Test alternative clearnet domains
    working_domains = await test_clearnet_alternatives()
    
    print(f"\n📊 SUMMARY")
    print(f"{'='*40}")
    
    if working_domains:
        print(f"✅ Found {len(working_domains)} working alternative domain(s):")
        for domain in working_domains:
            print(f"   🌐 {domain}")
        print(f"\n💡 These domains might have different rate limits!")
    else:
        print(f"❌ No alternative working domains found")
        print(f"⏳ Need to wait for rate limits to reset on main domain")
    
    print(f"\n🔧 RECOMMENDATIONS:")
    print(f"1. Wait 1-24 hours for main domain rate limits to reset")
    print(f"2. Consider setting up TOR proxy for .onion access")
    print(f"3. Register additional accounts if needed")
    print(f"4. Monitor rate limit reset times")

if __name__ == "__main__":
    asyncio.run(main())