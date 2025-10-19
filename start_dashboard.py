#!/usr/bin/env python3
"""
Startup script for the Prospect to Lead Workflow Dashboard
Launches the Flask web server with proper configuration
"""

import sys
import os
import webbrowser
import time
import threading

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def open_browser():
    """Open the browser after a short delay"""
    time.sleep(2)  # Wait 2 seconds for the server to start
    webbrowser.open('http://localhost:5000')

def main():
    """Main function to start the dashboard"""
    print("🚀 Prospect to Lead Workflow Dashboard")
    print("=" * 50)
    print("📊 Starting web server...")
    print("🌐 Dashboard will open at: http://localhost:5000")
    print("⏰ Please wait while the server initializes...")
    print("=" * 50)
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Import and run the Flask app
    try:
        from frontend.app import app
        print("\n✅ Server starting successfully!")
        print("💡 Press Ctrl+C to stop the server")
        print("🔄 The dashboard will refresh automatically every 2 seconds")
        print("-" * 50)
        
        # Run the Flask app
        app.run(
            debug=False,  # Set to False for cleaner output
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to prevent double startup
        )
    except Exception as e:
        print(f"❌ Error starting the dashboard: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check if port 5000 is already in use")
        print("3. Ensure you're in the correct directory")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())