# SIUC-003: Isolated Book Metadata Normalization
import sys
import json
sys.path.append('/home/almaz/microservices/zlibrary_api_module/')
from book_normalization_system import normalize_book_data # Hypothetical function

# --- Test Configuration ---
RAW_DATA_PATH = "/home/almaz/microservices/zlibrary_api_module/simplified_iuc/test_data/raw_book_data.json"

# --- Execution ---
print("Executing SIUC-03: Isolated Book Metadata Normalization")
with open(RAW_DATA_PATH, 'r') as f:
    raw_data = json.load(f)
    
try:
    normalized_data = normalize_book_data(raw_data)
    print(f"Normalized data: {normalized_data}")
except Exception as e:
    print(f"FAIL: Normalization function raised an exception: {e}")
    sys.exit(1)
    
# --- Verification ---
expected_keys = ["title", "authors", "year", "size", "extension"]
actual_keys = list(normalized_data.keys())

if not all(key in actual_keys for key in expected_keys):
    print("FAIL: Normalized data is missing one or more expected keys.")
    print(f"Expected: {expected_keys}")
    print(f"Got:      {actual_keys}")
    sys.exit(1)
    
if normalized_data.get('title') != "The Midnight Library":
    print(f"FAIL: Title was not normalized correctly.")
    sys.exit(1)

print("PASS: Metadata normalization test successful.")
sys.exit(0)
