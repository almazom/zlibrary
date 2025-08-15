
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

        paginator = await lib.profile.search_public_booklists(q="science", count=5)
        booklists = await paginator.next()

        assert isinstance(booklists, list)
        print(f"Found {len(booklists)} public booklists.")
        print("Public booklist retrieval test passed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await lib.session.close()


if __name__ == "__main__":
    asyncio.run(main())
