"""
ErgoAnalyzer Launcher - Standalone executable
This launches the Flask server and opens the browser
"""

import os
import sys
import time
import webbrowser
import subprocess
import threading

def get_app_path():
    """Get the path to the application directory."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def open_browser_delayed():
    """Open browser after a delay to let server start."""
    time.sleep(5)
    webbrowser.open('http://localhost:5000')

def main():
    app_path = get_app_path()
    os.chdir(app_path)
    
    print("=" * 60)
    print("  ErgoAnalyzer - Ergonomic Posture Analysis System")
    print("  RULA & REBA Assessment Tool")
    print("=" * 60)
    print()
    print("Starting server... Please wait.")
    print()
    print("Your browser will open automatically.")
    print("Keep this window open while using the application.")
    print()
    print("Press Ctrl+C to stop the server.")
    print()
    print("=" * 60)
    
    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
    browser_thread.start()
    
    # Import and run the Flask app
    try:
        # Add app path to Python path
        sys.path.insert(0, app_path)
        
        from app import app
        
        # Run Flask server
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nPress Enter to exit...")
        input()

if __name__ == '__main__':
    main()
