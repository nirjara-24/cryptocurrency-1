import sys
import os
import traceback

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    import initialize
    print("Starting initialization...")
    initialize.initialize()
    print("Initialization finished successfully.")
except Exception as e:
    print(f"\n❌ Initialization failed with error: {e}")
    traceback.print_exc()
