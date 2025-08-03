#!/usr/bin/env python3
"""
Start all stubbed servers for testing.

This script launches all the MCP servers on different ports so they can
be tested together.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Server configurations
SERVERS = [
    {
        "name": "FamilySearch API Server",
        "script": "servers/familysearch-api/server.py",
        "port": 8001,
        "description": "Handles FamilySearch API interactions"
    },
    {
        "name": "Records Router",
        "script": "servers/records-router/server.py", 
        "port": 8002,
        "description": "Routes searches across multiple providers"
    },
    {
        "name": "Document Processing",
        "script": "servers/document-processing/server.py",
        "port": 8003,
        "description": "Processes and extracts data from documents"
    },
    {
        "name": "Analysis Server",
        "script": "servers/analysis/server.py",
        "port": 8004,
        "description": "Analyzes genealogical data and provides insights"
    },
    {
        "name": "Research Management",
        "script": "servers/research-management/server.py",
        "port": 8005,
        "description": "Manages research projects and tasks"
    },
    {
        "name": "Location Server",
        "script": "servers/location/server.py",
        "port": 8006,
        "description": "Handles place information and geographic context"
    }
]

# Global process list for cleanup
processes = []

def start_server(server_config):
    """Start a single server in a separate process."""
    name = server_config["name"]
    script = server_config["script"]
    port = server_config["port"]
    
    print(f"🚀 Starting {name} on port {port}...")
    
    try:
        # Start the server process
        process = subprocess.Popen([
            sys.executable, script
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        processes.append(process)
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"   ✅ {name} started successfully")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ {name} failed to start")
            print(f"      stdout: {stdout.decode()}")
            print(f"      stderr: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error starting {name}: {e}")
        return False

def cleanup_processes():
    """Clean up all running processes."""
    print("\n🛑 Stopping all servers...")
    
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            print(f"Error stopping process: {e}")

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    print("\n⚠️  Received interrupt signal, shutting down...")
    cleanup_processes()
    sys.exit(0)

def main():
    """Start all servers."""
    print("🚀 Starting All Stubbed Servers")
    print("=" * 50)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if all server scripts exist
    missing_scripts = []
    for server in SERVERS:
        if not Path(server["script"]).exists():
            missing_scripts.append(server["script"])
    
    if missing_scripts:
        print("❌ Missing server scripts:")
        for script in missing_scripts:
            print(f"   - {script}")
        print("\nPlease ensure all server scripts exist before starting.")
        return
    
    # Start all servers
    started_servers = []
    failed_servers = []
    
    for server in SERVERS:
        if start_server(server):
            started_servers.append(server)
        else:
            failed_servers.append(server)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Server Startup Summary:")
    
    if started_servers:
        print(f"✅ Started {len(started_servers)} servers:")
        for server in started_servers:
            print(f"   - {server['name']} (port {server['port']})")
    
    if failed_servers:
        print(f"❌ Failed to start {len(failed_servers)} servers:")
        for server in failed_servers:
            print(f"   - {server['name']} (port {server['port']})")
    
    if started_servers:
        print(f"\n🎉 Successfully started {len(started_servers)} servers!")
        print("\n📋 Server URLs:")
        for server in started_servers:
            print(f"   {server['name']}: http://localhost:{server['port']}")
        
        print(f"\n🧪 Test the integration:")
        print(f"   python scripts/test_all_servers.py")
        
        print(f"\n⏹️  Press Ctrl+C to stop all servers")
        
        try:
            # Keep the main process running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("❌ No servers started successfully.")
        print("Check the error messages above and try again.")

if __name__ == "__main__":
    main() 