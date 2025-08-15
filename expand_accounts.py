#!/usr/bin/env python3
"""
Expand the Z-Library multi-account configuration with additional accounts
"""

import re

def create_additional_accounts():
    """Generate additional Z-Library account configurations"""
    
    # Additional accounts to add to the pool
    additional_accounts = [
        "('almazomam4@gmail.com', 'tataronrails78'),",
        "('almazomam5@gmail.com', 'tataronrails78'),", 
        "('almazomam6@gmail.com', 'tataronrails78'),",
        "('almazomam7@gmail.com', 'tataronrails78'),",
        "('almazomam8@gmail.com', 'tataronrails78'),",
        "('almazomam9@gmail.com', 'tataronrails78'),",
        "('almazomam10@gmail.com', 'tataronrails78'),",
        "# Add more accounts as needed",
        "# ('newaccount@gmail.com', 'password'),",
    ]
    
    return additional_accounts

def update_book_search_engine():
    """Update the book_search_engine.py with expanded accounts"""
    
    file_path = "scripts/book_search_engine.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the accounts section
    accounts_pattern = r'(accounts = \[\s*)(.*?)(\s*\])'
    
    def replace_accounts(match):
        start = match.group(1)
        end = match.group(3)
        
        # Current accounts
        current_accounts = [
            "('almazomam@gmail.com', 'tataronrails78'),",
            "('almazomam2@gmail.com', 'tataronrails78'),",
            "('almazomam3@gmail.com', 'tataronrails78'),"
        ]
        
        # Additional accounts
        additional = create_additional_accounts()
        
        # Combine all accounts
        all_accounts = current_accounts + additional
        account_lines = '\n        '.join(all_accounts)
        
        return f"{start}\n        {account_lines}\n    {end}"
    
    # Replace the accounts section
    updated_content = re.sub(accounts_pattern, replace_accounts, content, flags=re.DOTALL)
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated book_search_engine.py with expanded account pool")
    print("📊 Now configured with 10+ accounts for better availability")

def show_account_management_tips():
    """Show tips for managing multiple Z-Library accounts"""
    
    print("\n🎯 Z-Library Multi-Account Management Tips")
    print("="*60)
    print("1. 📅 Each account gets 10 downloads per day")
    print("2. 🔄 Downloads reset every 24 hours")
    print("3. 🔀 Script tries accounts in order until one works")
    print("4. 📈 More accounts = higher availability")
    print("5. ⚡ Failed accounts are skipped automatically")
    print("\n💡 To add new accounts:")
    print("   - Register new Z-Library accounts")
    print("   - Add them to the accounts list in book_search_engine.py")
    print("   - Format: ('email@domain.com', 'password'),")
    print("\n🔍 To check account status:")
    print("   python3 check_account_limits.py")

if __name__ == "__main__":
    print("🚀 Expanding Z-Library Multi-Account Configuration")
    print("="*60)
    
    update_book_search_engine()
    show_account_management_tips()
    
    print(f"\n✅ Multi-account setup expanded!")
    print("🔄 Accounts will reset in ~4 hours")
    print("📝 Consider registering additional Z-Library accounts for 24/7 availability")