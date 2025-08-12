#!/usr/bin/env python3
"""
Test alternative Z-Library domains with our accounts
Check if they have different rate limits
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_domain_with_account(session, domain, email, password):
    """Test login on a specific domain"""
    
    # Construct login URL for domain
    if domain.endswith('/'):
        login_url = domain + "rpc.php"
    else:
        login_url = domain + "/rpc.php"
    
    print(f"📡 Testing login on: {login_url}")
    print(f"👤 Account: {email}")
    
    data = {
        "isModal": True,
        "email": email,
        "password": password,
        "action": "login",
        "redirectUrl": "",
        "gg_json_mode": 1,
    }
    
    try:
        async with session.post(login_url, data=data) as response:
            print(f"  📊 HTTP Status: {response.status}")
            
            if response.status != 200:
                print(f"  ❌ HTTP Error: {response.status}")
                return False, f"HTTP {response.status}"
            
            text = await response.text()
            print(f"  📝 Response length: {len(text)} characters")
            
            if not text:
                print(f"  ❌ Empty response")
                return False, "Empty response"
            
            try:
                json_resp = json.loads(text)
                print(f"  📋 Response structure: {json.dumps(json_resp, indent=2)}")
                
                # Check for errors
                if 'errors' in json_resp and json_resp['errors']:
                    for error in json_resp['errors']:
                        code = error.get('code', 'Unknown')
                        message = error.get('message', 'Unknown')
                        
                        if code == 99 and "too many logins" in message.lower():
                            print(f"  🔴 RATE LIMITED: {message}")
                            return False, "Rate limited"
                        elif code == 1:
                            print(f"  ❌ AUTH FAILED: {message}")
                            return False, "Auth failed"
                        else:
                            print(f"  🔍 OTHER ERROR: {message}")
                            return False, f"Error {code}: {message}"
                
                # Check for success
                elif 'response' in json_resp:
                    if json_resp['response'] is not None:
                        print(f"  🟢 SUCCESS! Login successful on this domain!")
                        return True, "Success"
                    else:
                        print(f"  🔴 FAILED: Null response")
                        return False, "Null response"
                else:
                    print(f"  🟡 UNKNOWN: Unexpected response format")
                    return False, "Unknown format"
                    
            except json.JSONDecodeError:
                print(f"  ❌ Invalid JSON response")
                print(f"  📄 Raw text: {text[:200]}...")
                return False, "Invalid JSON"
                
    except asyncio.TimeoutError:
        print(f"  ⏰ Request timeout")
        return False, "Timeout"
    except aiohttp.ClientError as e:
        print(f"  🌐 Network error: {e}")
        return False, f"Network error: {e}"
    except Exception as e:
        print(f"  💥 Unexpected error: {e}")
        return False, f"Unexpected error: {e}"

async def test_all_domains_and_accounts():
    """Test all alternative domains with all accounts"""
    
    # Domains to test
    domains = [
        "https://z-library.sk",          # Original (known rate limited)
        "https://zlibrary-global.se",    # Alternative 1
        "https://1lib.sk"                # Alternative 2
    ]
    
    # Test account
    test_account = {
        "email": "almazomam2@gmail.com",
        "password": "tataronrails78"
    }
    
    print(f"🔍 Testing Multiple Z-Library Domains")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Test account: {test_account['email']}")
    print()
    
    results = []
    
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        for i, domain in enumerate(domains, 1):
            print(f"{'='*60}")
            print(f"🧪 TESTING DOMAIN {i}/{len(domains)}: {domain}")
            print(f"{'='*60}")
            
            success, message = await test_domain_with_account(
                session, domain, test_account['email'], test_account['password']
            )
            
            result = {
                'domain': domain,
                'success': success,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            
            # Add delay between domain tests
            if i < len(domains):
                print(f"\n⏳ Waiting 3 seconds before next domain...")
                await asyncio.sleep(3)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 DOMAIN TESTING SUMMARY")
    print(f"{'='*80}")
    
    working_domains = []
    rate_limited_domains = []
    failed_domains = []
    
    for result in results:
        domain = result['domain']
        success = result['success']
        message = result['message']
        
        if success:
            print(f"🟢 {domain}: SUCCESS - {message}")
            working_domains.append(domain)
        elif "rate limited" in message.lower():
            print(f"🔴 {domain}: RATE LIMITED - {message}")
            rate_limited_domains.append(domain)
        else:
            print(f"❌ {domain}: FAILED - {message}")
            failed_domains.append(domain)
    
    print(f"\n📈 Results:")
    print(f"✅ Working domains: {len(working_domains)}")
    print(f"🔴 Rate limited domains: {len(rate_limited_domains)}")
    print(f"❌ Failed domains: {len(failed_domains)}")
    
    if working_domains:
        print(f"\n🎉 GREAT NEWS! Found working domain(s):")
        for domain in working_domains:
            print(f"   🌐 {domain}")
        print(f"\n💡 We can update the system to use these domains!")
        
        # Save working domains to file
        working_domains_file = f"working_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(working_domains_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'working_domains': working_domains,
                'test_results': results
            }, f, indent=2)
        print(f"💾 Working domains saved to: {working_domains_file}")
        
    else:
        print(f"\n😔 No working domains found")
        print(f"⏳ All domains appear to share the same rate limiting")
        print(f"🕐 Need to wait for rate limits to reset")
    
    return working_domains

if __name__ == "__main__":
    working = asyncio.run(test_all_domains_and_accounts())
    if working:
        print(f"\n🚀 NEXT STEPS:")
        print(f"1. Update zlibrary client to use working domain")
        print(f"2. Test book search with working domain")
        print(f"3. Run UC29 test successfully!")
    else:
        print(f"\n⏳ WAIT AND RETRY:")
        print(f"1. All domains are rate limited")
        print(f"2. Wait 1-24 hours for reset")
        print(f"3. System is ready when limits reset")