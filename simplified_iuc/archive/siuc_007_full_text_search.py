
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

        # Using a common phrase to ensure results
        paginator = await lib.full_text_search(q="a long time ago in a galaxy far far away", count=1)
        results = await paginator.next()

        assert isinstance(results, list)
        print(f"Found {len(results)} results in full-text search.")
        print("Full-text search test passed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await lib.session.close()


if __name__ == "__main__":
    asyncio.run(main())
