#!/usr/bin/env python3

import asyncio
import os
from zlibrary import AsyncZlib
from dotenv import load_dotenv

async def search_and_download_book():
    # Load environment variables
    load_dotenv()
    
    email = os.getenv('ZLOGIN')
    password = os.getenv('ZPASSW')
    
    if not email or not password:
        print("Please set ZLOGIN and ZPASSW environment variables")
        return
    
    # Initialize client
    client = AsyncZlib()
    
    try:
        # Login
        print("Logging in to Z-Library...")
        profile = await client.login(email, password)
        print(f"✓ Logged in successfully")
        
        # Check download limits
        limits = await profile.get_limits()
        print(f"Download limits: {limits['daily_remaining']}/{limits['daily_allowed']} remaining today")
        print()
        
        # Search for the book
        search_query = "All the Other Mothers Hate Me Sarah Harman"
        print(f"Searching for: '{search_query}'")
        print("-" * 60)
        
        results = await client.search(q=search_query, count=10)
        await results.init()
        
        if not results.result:
            print("No results found. Trying alternative search...")
            # Try searching with just the title
            results = await client.search(q="All the Other Mothers Hate Me", count=10)
            await results.init()
        
        if results.result:
            print(f"Found {len(results.result)} results on page {results.page}/{results.total}:\n")
            
            # Display all results
            for idx, book in enumerate(results.result, 1):
                print(f"{idx}. {book.title}")
                print(f"   Author: {book.authors}")
                print(f"   Year: {book.year}")
                print(f"   Format: {book.extension}")
                print(f"   Size: {book.size}")
                print(f"   ID: {book.id}")
                print()
            
            # Ask user to select a book
            if len(results.result) == 1:
                choice = 1
                print("Only one result found, selecting it automatically...")
            else:
                try:
                    choice = int(input(f"Select book to download (1-{len(results.result)}): "))
                    if choice < 1 or choice > len(results.result):
                        print("Invalid selection")
                        return
                except ValueError:
                    print("Invalid input")
                    return
            
            # Fetch detailed information for selected book
            selected_book = results.result[choice - 1]
            print(f"\nFetching details for: {selected_book.title}")
            details = await selected_book.fetch()
            
            print("\nDetailed Information:")
            print("-" * 60)
            print(f"Title: {details.get('name', 'N/A')}")
            print(f"Authors: {', '.join([a.get('name', '') for a in details.get('authors', [])])}")
            print(f"Year: {details.get('year', 'N/A')}")
            print(f"Publisher: {details.get('publisher', 'N/A')}")
            print(f"Language: {details.get('language', 'N/A')}")
            print(f"Extension: {details.get('extension', 'N/A')}")
            print(f"Size: {details.get('size', 'N/A')}")
            print(f"Description: {details.get('description', 'N/A')[:200]}...")
            print(f"Categories: {details.get('categories', 'N/A')}")
            print(f"ISBN: {details.get('isbn10', 'N/A')} / {details.get('isbn13', 'N/A')}")
            
            # Download URL
            download_url = details.get('download_url', '')
            if download_url and 'dl2.php' in download_url:
                print(f"\n✓ Download available!")
                print(f"Download URL: {download_url}")
                print("\nYou can download the book by:")
                print("1. Opening the URL in your browser (you must be logged in)")
                print("2. Using wget/curl with the appropriate cookies")
                
                # Optional: Auto-download with requests (would need additional implementation)
                download_choice = input("\nWould you like to copy the download URL to clipboard? (y/n): ")
                if download_choice.lower() == 'y':
                    try:
                        import pyperclip
                        pyperclip.copy(download_url)
                        print("✓ Download URL copied to clipboard!")
                    except ImportError:
                        print("Install pyperclip to enable clipboard functionality: pip install pyperclip")
            else:
                print(f"\n✗ Download not available or book is restricted")
                print(f"Status: {download_url if download_url else 'No download URL'}")
                
        else:
            print("No results found for this book.")
            print("\nSuggestions:")
            print("- Try searching with just the title")
            print("- Check spelling")
            print("- Try alternative keywords")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.logout()
        print("\n✓ Logged out")

if __name__ == "__main__":
    asyncio.run(search_and_download_book())