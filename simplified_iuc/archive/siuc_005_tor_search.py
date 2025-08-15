
import asyncio
import os
import zlibrary

async def main():
    email = os.environ.get("ZLIB_EMAIL")
    password = os.environ.get("ZLIB_PASSWORD")

    if not email or not password:
        print("ZLIB_EMAIL and ZLIB_PASSWORD environment variables must be set.")
        return

    # This test assumes a Tor proxy is running on the default port 9050.
    lib = zlibrary.AsyncZlib(onion=True, proxy_list=['socks5://127.0.0.1:9050'])
    try:
        await lib.login(email, password)
        print("Login successful through Tor.")

        paginator = await lib.search(q="python", count=1)
        results = await paginator.next()

        assert isinstance(results, list)
        assert len(results) > 0
        print("Tor search test passed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await lib.session.close()


if __name__ == "__main__":
    asyncio.run(main())
