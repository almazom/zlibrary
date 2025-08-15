
import asyncio
import os
import zlibrary

async def main():
    email = os.environ.get("ZLIB_EMAIL")
    password = os.environ.get("ZLIB_PASSWORD")

    if not email or not password:
        print("ZLIB_EMAIL and ZLIB_PASSWORD environment variables must be set.")
        return

    lib = zlibrary.AsyncZlib()
    try:
        await lib.login(email, password)
        print("Login successful.")

        # 1. Search for public booklists
        booklist_paginator = await lib.profile.search_public_booklists(q="python", count=1)
        booklists = await booklist_paginator.next()
        print(f"Found {len(booklists)} booklists.")

        if not booklists:
            print("No booklists found, cannot proceed with test.")
            return

        # 2. Get the first booklist
        first_booklist = booklists[0]
        await first_booklist.fetch() # Fetch booklist details

        # 3. Get the books from that booklist
        books_in_list = await first_booklist.next()
        print(f"Found {len(books_in_list)} books in the first booklist.")

        if not books_in_list:
            print("No books found in the booklist, cannot proceed.")
            return

        # 4. Fetch the details of the first book
        first_book = books_in_list[0]
        book_details = await first_book.fetch()

        assert book_details is not None
        assert "name" in book_details
        print(f"Successfully fetched details for book: {book_details['name']}")
        print("Fetch book from booklist test passed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await lib.session.close()


if __name__ == "__main__":
    asyncio.run(main())
