
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

        paginator = await lib.search(q="history", count=2)
        
        first_page_results = await paginator.next()
        print(f"First page has {len(first_page_results)} results.")

        second_page_results = await paginator.next()
        print(f"Second page has {len(second_page_results)} results.")

        # Navigate back to the first page
        prev_page_results = await paginator.prev()
        print(f"Previous page has {len(prev_page_results)} results.")

        assert first_page_results == prev_page_results
        print("Paginator navigation test passed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await lib.session.close()


if __name__ == "__main__":
    asyncio.run(main())
