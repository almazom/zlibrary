#!/usr/bin/env python3
"""
Z-Library Account Health Monitor
Checks status of all configured accounts
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib

async def check_all_accounts():
    """Check status of all Z-Library accounts"""
    
    accounts = [
        ('almazomam@gmail.com', 'tataronrails78'),
        ('almazomam2@gmail.com', 'tataronrails78'),
        ('almazomam3@gmail.com', 'tataronrails78')
    ]
    
    accounts_status = []
    total_available = 0
    total_limit = 0
    
    for i, (email, password) in enumerate(accounts):
        try:
            client = AsyncZlib()
            profile = await client.login(email, password)
            limits = await profile.get_limits()
            
            daily_remaining = limits.get('daily_remaining', 0)
            daily_allowed = limits.get('daily_allowed', 0)
            
            status = {
                "account_id": i + 1,
                "email": email.split('@')[0] + "@...",  # Privacy
                "daily_remaining": daily_remaining,
                "daily_limit": daily_allowed,
                "daily_used": daily_allowed - daily_remaining,
                "reset_time": limits.get('daily_reset', 'unknown'),
                "status": "healthy" if daily_remaining > 0 else "exhausted",
                "percentage_used": round((daily_allowed - daily_remaining) / daily_allowed * 100, 1) if daily_allowed > 0 else 0
            }
            
            total_available += daily_remaining
            total_limit += daily_allowed
            accounts_status.append(status)
            
            await client.logout()
            
        except Exception as e:
            accounts_status.append({
                "account_id": i + 1,
                "email": email.split('@')[0] + "@...",
                "status": "error",
                "error": str(e)[:100]  # Limit error message length
            })
    
    # Calculate overall health
    overall_health = "healthy"
    if total_available == 0:
        overall_health = "exhausted"
    elif total_available < 5:
        overall_health = "low"
    elif any(acc.get('status') == 'error' for acc in accounts_status):
        overall_health = "degraded"
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_downloads_available": total_available,
            "total_downloads_limit": total_limit,
            "total_downloads_used": total_limit - total_available,
            "overall_health": overall_health,
            "accounts_working": sum(1 for acc in accounts_status if acc.get('status') != 'error'),
            "accounts_total": len(accounts)
        },
        "accounts": accounts_status,
        "recommendation": get_recommendation(total_available, overall_health)
    }

def get_recommendation(downloads_available, health):
    """Get recommendation based on account status"""
    if health == "exhausted":
        return "All accounts exhausted. Wait for daily reset at midnight Moscow time."
    elif health == "low":
        return f"Only {downloads_available} downloads remaining. Use wisely."
    elif health == "degraded":
        return "Some accounts failing. Check credentials."
    else:
        return f"{downloads_available} downloads available. System healthy."

async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        # Quick summary mode
        result = await check_all_accounts()
        summary = result['summary']
        print(f"Total: {summary['total_downloads_available']}/{summary['total_downloads_limit']} downloads")
        print(f"Health: {summary['overall_health']}")
    else:
        # Full JSON output
        result = await check_all_accounts()
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())