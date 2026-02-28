"""
Heartbeat Monitor - Detects Application Stalls

This module provides a thread-based monitoring system that detects when the
application stops making progress and forces an exit to prevent indefinite hanging.

Usage:
    from utils.heartbeat_monitor import HeartbeatMonitor
    
    monitor = HeartbeatMonitor(stall_threshold_seconds=180)
    monitor.start()
    
    try:
        monitor.beat("Starting workflow")
        # ... do work ...
        monitor.beat("Step 1 complete")
        # ... more work ...
        monitor.beat("Step 2 complete")
    finally:
        monitor.stop()
"""

import threading
import time
import sys
import os
from datetime import datetime


class HeartbeatMonitor:
    """
    Monitors application progress and detects stalls.
    
    If no heartbeat is received within the stall threshold, the monitor
    will force the application to exit with code 1.
    """
    
    def __init__(self, stall_threshold_seconds: int = 180, check_interval: int = 10):
        """
        Initialize the heartbeat monitor.
        
        Args:
            stall_threshold_seconds: Maximum time without heartbeat before considering stalled (default: 180s = 3 minutes)
            check_interval: How often to check for stalls in seconds (default: 10s)
        """
        self.stall_threshold = stall_threshold_seconds
        self.check_interval = check_interval
        self.last_heartbeat = time.time()
        self.start_time = time.time()
        self.running = False
        self.thread = None
        self.beat_count = 0
        
    def start(self):
        """Start the heartbeat monitor in a background thread."""
        if self.running:
            return
            
        self.running = True
        self.start_time = time.time()
        self.last_heartbeat = time.time()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        print(f"💓 Heartbeat monitor started")
        print(f"   Stall threshold: {self.stall_threshold}s ({self.stall_threshold/60:.1f} minutes)")
        print(f"   Check interval: {self.check_interval}s")
        print()
        
    def beat(self, message: str = ""):
        """
        Update the heartbeat timestamp.
        
        Args:
            message: Optional progress message to display
        """
        self.last_heartbeat = time.time()
        self.beat_count += 1
        
        elapsed = self.last_heartbeat - self.start_time
        
        if message:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"💓 [{timestamp}] {message} (elapsed: {elapsed:.1f}s)")
        
    def stop(self):
        """Stop the heartbeat monitor."""
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
            
        elapsed = time.time() - self.start_time
        print()
        print(f"💓 Heartbeat monitor stopped")
        print(f"   Total beats: {self.beat_count}")
        print(f"   Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        
    def _monitor_loop(self):
        """
        Background monitoring loop.
        
        Checks periodically if the application has stalled and forces exit if needed.
        """
        while self.running:
            current_time = time.time()
            elapsed_since_beat = current_time - self.last_heartbeat
            total_elapsed = current_time - self.start_time
            
            # Check if stalled
            if elapsed_since_beat > self.stall_threshold:
                print()
                print("=" * 80)
                print("⚠️  STALL DETECTED - APPLICATION APPEARS TO BE HUNG")
                print("=" * 80)
                print(f"   Time since last heartbeat: {elapsed_since_beat:.1f}s ({elapsed_since_beat/60:.1f} minutes)")
                print(f"   Stall threshold: {self.stall_threshold}s ({self.stall_threshold/60:.1f} minutes)")
                print(f"   Total elapsed time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
                print(f"   Total heartbeats received: {self.beat_count}")
                print()
                print("Possible causes:")
                print("   1. API call to Anthropic is hanging")
                print("   2. Network connectivity issues")
                print("   3. Blocking operation in MCP Agent Cloud library")
                print()
                print("Forcing application exit...")
                print("=" * 80)
                print()
                
                # Force exit
                os._exit(1)
                
            # Sleep until next check
            time.sleep(self.check_interval)


# Convenience function for simple usage
def monitor_execution(func, stall_threshold_seconds: int = 180):
    """
    Decorator to monitor a function execution with heartbeat.
    
    Args:
        func: Async function to monitor
        stall_threshold_seconds: Stall threshold in seconds
        
    Returns:
        Wrapped function with heartbeat monitoring
    """
    async def wrapper(*args, **kwargs):
        monitor = HeartbeatMonitor(stall_threshold_seconds=stall_threshold_seconds)
        monitor.start()
        
        try:
            monitor.beat(f"Starting {func.__name__}")
            result = await func(*args, **kwargs)
            monitor.beat(f"Completed {func.__name__}")
            return result
        finally:
            monitor.stop()
            
    return wrapper

