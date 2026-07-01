# core/recovery/cleaner.py
import os

def kill_zombie_processes():
    """Kills leftover ffmpeg or aria2c processes to prevent memory leaks."""
    print("🧹 Sweeping environment for zombie processes...")
    # Suppressing stderr so it doesn't print messy errors if no processes are found
    os.system("pkill -9 ffmpeg 2>/dev/null")
    os.system("pkill -9 aria2c 2>/dev/null")
    os.system("pkill -9 mediago 2>/dev/null")
    print("✅ Environment is clean.")
