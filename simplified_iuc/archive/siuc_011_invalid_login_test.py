# SIUC-011: Invalid Login Attempt Test
import asyncio
import sys
import zlibrary

# --- Test Configuration ---
INVALID_EMAIL = "invalid_email@example.com"
INVALID_PASSWORD = "invalid_password_for_test"

# --- Execution ---
print("Executing SIUC-011: Invalid Login Attempt Test")
lib = zlibrary.AsyncZlib()
try:
    # This is expected to fail
    asyncio.run(lib.login(INVALID_EMAIL, INVALID_PASSWORD))
    # If this line is reached, the test has failed because no exception was thrown.
    print("FAIL: Login succeeded with invalid credentials.")
    # --- Verification ---
    print("Expected an exception to be raised, but none was.")
    sys.exit(1)

except Exception as e:
    # --- Verification ---
    # An exception is the expected outcome.
    print(f"Successfully caught expected exception: {e}")
    print("PASS: Library correctly handled invalid login attempt.")
    sys.exit(0)

finally:
    asyncio.run(lib.session.close())