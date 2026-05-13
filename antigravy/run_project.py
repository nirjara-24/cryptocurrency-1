import subprocess
import time
import sys
import os

def run_project():
    print("🚀 Starting Cryptocurrency Analysis Project...")
    
    # 0. Check Dependencies
    print("\n📦 Checking dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"⚠️ Warning: Could not complete dependency check: {e}")

    # 1. Start Backend
    print("\n🖥️ Starting Backend API (Flask)...")
    try:
        backend = subprocess.Popen([sys.executable, "backend/app.py"])
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return

    # 2. Start Frontend
    print("\n🌐 Starting Frontend Server (http://localhost:8080)...")
    try:
        frontend = subprocess.Popen([sys.executable, "-m", "http.server", "8080", "--directory", "frontend"])
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        backend.terminate()
        return

    print("\n📦 Initializing/Updating Database in background...")
    print(" (This handles data collection and model training for 10 assets)")
    # Start initialization in background so it doesn't block the UI
    try:
        init_process = subprocess.Popen([sys.executable, "initialize.py"])
    except Exception as e:
        print(f"⚠️ Warning: Failed to start background initialization: {e}")
        init_process = None

    print("\n✅ Project is live!")
    print("👉 Access the dashboard at: http://localhost:8080")
    print("👉 API health check at: http://localhost:5000/api/status")
    print("\nInitialization will continue in the background. Data will populate as it's ready.")
    print("Press Ctrl+C to stop all services.")

    try:
        while True:
            # Check if any process has died
            if backend.poll() is not None:
                print("❌ Backend server stopped unexpectedly.")
                break
            if frontend.poll() is not None:
                print("❌ Frontend server stopped unexpectedly.")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
    finally:
        backend.terminate()
        frontend.terminate()
        if init_process:
            init_process.terminate()
        print("Done.")

if __name__ == "__main__":
    run_project()
