#!/usr/bin/env python3
"""
Test all Z-Library accounts individually using direct HTTP requests
Check rate limiting status and account health
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

async def test_account_login(session, account_info, account_num):
    """Test individual account login via direct API call"""
    
    email = account_info['email']
    password = account_info['password']
    
    print(f"\n{'='*60}")
    print(f"🧪 TESTING ACCOUNT {account_num}/3: {email}")
    print(f"{'='*60}")
    
    # Z-Library login endpoint
    login_url = "https://z-library.sk/rpc.php"
    
    # Login data
    data = {
        "isModal": True,
        "email": email,
        "password": password,
        "action": "login",
        "redirectUrl": "",
        "gg_json_mode": 1,
    }
    
    try:
        print(f"📡 Sending login request to: {login_url}")
        print(f"👤 Email: {email}")
        print(f"🔑 Password: {'*' * len(password)}")
        
        # Record start time
        start_time = time.time()
        
        async with session.post(login_url, data=data) as response:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            print(f"⏱️  Response time: {response_time}ms")
            print(f"📊 HTTP Status: {response.status}")
            print(f"🌐 Headers: {dict(response.headers)}")
            
            # Get response text
            text = await response.text()
            print(f"📝 Response length: {len(text)} characters")
            
            if text:
                try:
                    json_resp = json.loads(text)
                    print(f"✅ Valid JSON response")
                    print(f"📋 Response structure: {json.dumps(json_resp, indent=2)}")
                    
                    # Analyze response
                    if 'errors' in json_resp and json_resp['errors']:
                        errors = json_resp['errors']
                        print(f"\n🔴 ERRORS DETECTED:")
                        for i, error in enumerate(errors, 1):
                            code = error.get('code', 'Unknown')
                            message = error.get('message', 'Unknown error')
                            print(f"  {i}. Code {code}: {message}")
                            
                            # Analyze specific error types
                            if code == 99:
                                if "too many logins" in message.lower():
                                    print(f"    🚫 RATE LIMITED - Account temporarily blocked")
                                    return "rate_limited", message
                                else:
                                    print(f"    ⚠️  Login restriction - {message}")
                                    return "restricted", message
                            elif code == 1:
                                print(f"    ❌ Authentication failed - Invalid credentials")
                                return "auth_failed", message
                            else:
                                print(f"    🔍 Other error - {message}")
                                return "other_error", message
                    
                    elif 'response' in json_resp:
                        if json_resp['response'] is None:
                            print(f"\n🔴 NULL RESPONSE - Likely rate limited")
                            return "rate_limited", "Response is null"
                        else:
                            response_data = json_resp['response']
                            print(f"\n🟢 SUCCESS - Login appears successful!")
                            print(f"📊 Response data: {json.dumps(response_data, indent=2)}")
                            return "success", "Login successful"
                    
                    else:
                        print(f"\n🟡 UNKNOWN RESPONSE FORMAT")
                        return "unknown", "Unexpected response format"
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response")
                    print(f"📄 Raw text: {text[:500]}...")
                    return "invalid_json", "Response is not valid JSON"
            else:
                print(f"❌ Empty response")
                return "empty_response", "No response received"
                
    except asyncio.TimeoutError:
        print(f"⏰ Request timed out")
        return "timeout", "Request timed out"
    except aiohttp.ClientError as e:
        print(f"🌐 Network error: {e}")
        return "network_error", str(e)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return "unexpected_error", str(e)

async def test_all_accounts():
    """Test all accounts from config file"""
    
    print(f"🔍 Z-Library Account Testing Suite")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Testing against: https://z-library.sk/")
    
    # Load accounts from config
    with open('accounts_config.json', 'r') as f:
        config = json.load(f)
    
    accounts = config.get('accounts', [])
    active_accounts = [acc for acc in accounts if acc.get('is_active', False)]
    
    print(f"📊 Total accounts in config: {len(accounts)}")
    print(f"🟢 Active accounts: {len(active_accounts)}")
    
    if not active_accounts:
        print(f"❌ No active accounts found!")
        return
    
    # Test results
    results = []
    
    # Create session with timeout
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        for i, account in enumerate(active_accounts, 1):
            status, message = await test_account_login(session, account, i)
            
            result = {
                'account_number': i,
                'email': account['email'],
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            
            # Add delay between tests to avoid additional rate limiting
            if i < len(active_accounts):
                print(f"\n⏳ Waiting 3 seconds before next test...")
                await asyncio.sleep(3)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 TESTING SUMMARY")
    print(f"{'='*80}")
    
    status_counts = {}
    for result in results:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"📈 Results breakdown:")
    for status, count in status_counts.items():
        emoji = {
            'success': '🟢',
            'rate_limited': '🔴', 
            'auth_failed': '❌',
            'restricted': '🟡',
            'timeout': '⏰',
            'network_error': '🌐',
            'other_error': '🔍'
        }.get(status, '❓')
        print(f"   {emoji} {status}: {count} account(s)")
    
    print(f"\n📋 Detailed results:")
    for result in results:
        emoji = {
            'success': '🟢',
            'rate_limited': '🔴',
            'auth_failed': '❌', 
            'restricted': '🟡',
            'timeout': '⏰',
            'network_error': '🌐',
            'other_error': '🔍'
        }.get(result['status'], '❓')
        print(f"   {emoji} {result['email']}: {result['status']} - {result['message']}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    working_accounts = [r for r in results if r['status'] == 'success']
    rate_limited = [r for r in results if r['status'] == 'rate_limited']
    failed_auth = [r for r in results if r['status'] == 'auth_failed']
    
    if working_accounts:
        print(f"✅ {len(working_accounts)} account(s) are working - book search should succeed!")
    
    if rate_limited:
        print(f"⏳ {len(rate_limited)} account(s) are rate limited - wait 1-24 hours")
        
    if failed_auth:
        print(f"🔑 {len(failed_auth)} account(s) have authentication issues - check credentials")
    
    if not working_accounts:
        print(f"⚠️  No working accounts available - book search will fail until rate limits reset")
    
    # Save results to file
    results_file = f"account_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tested': len(results),
            'results': results,
            'summary': status_counts
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")

if __name__ == "__main__":
    asyncio.run(test_all_accounts())