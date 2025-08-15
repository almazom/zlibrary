
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

        history = await lib.profile.download_history()
        print(f"Found {len(history.result)} items in download history.")
        assert isinstance(history.result, list)
        print("Download history test passed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await lib.session.close()


if __name__ == "__main__":
    asyncio.run(main())
