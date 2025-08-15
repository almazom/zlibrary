# SIUC-002: Isolated Account Limit Check
import sys
import json
# Assuming 'check_account_limits.py' can be imported
# This might need path adjustments or packaging improvements
sys.path.append('/home/almaz/microservices/zlibrary_api_module/')
from check_account_limits import get_account_limits # Hypothetical function

# --- Test Configuration ---
# Store test credentials securely, not in the script itself.
# For this example, we use a placeholder.
TEST_ACCOUNT_EMAIL = "test_account_1@example.com"
TEST_ACCOUNT_PASSWORD = "test_password_1"

# --- Execution ---
print("Executing SIUC-002: Isolated Account Limit Check")
try:
    limits = get_account_limits(TEST_ACCOUNT_EMAIL, TEST_ACCOUNT_PASSWORD)
    print(f"Successfully retrieved limits: {limits}")
except Exception as e:
    print(f"FAIL: Script raised an exception: {e}")
    sys.exit(1)
    
# --- Verification ---
if "daily_remaining" not in limits or "daily_allowed" not in limits:
    print("FAIL: The returned dictionary is missing required keys.")
    print(f"Expected keys: 'daily_remaining', 'daily_allowed'")
    print(f"Got keys: {limits.keys()}")
    sys.exit(1)
    
print("PASS: Account limit check successful.")
sys.exit(0)
