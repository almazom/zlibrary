
import asyncio
import os
import zlibrary
from zlibrary import Language, Extension

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

        paginator = await lib.search(
            q="programming",
            lang=[Language.ENGLISH],
            extensions=[Extension.PDF],
            from_year=2020,
            to_year=2023
        )
        results = await paginator.next()

        assert isinstance(results, list)
        print(f"Found {len(results)} results with filters.")
        # Optional: Add more specific assertions here if you have expected results
        print("Search with filters test passed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await lib.session.close()


if __name__ == "__main__":
    asyncio.run(main())
