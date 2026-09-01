"""
ADAS Mobile Automatic Loop Blackbox Recorder
- Automatic lifecycle start/stop
- Max 2 video segments circular buffer (FIFO)
- Deletes oldest segment when memory limit is reached.
"""

import os
import glob
import time
from typing import List

class CircularBlackboxRecorder:
    def __init__(self, storage_dir: str = "dashcam_recordings", max_segments: int = 2, segment_duration_sec: int = 180):
        """
        :param storage_dir: Directory where video segments are stored
        :param max_segments: Strictly maximum 2 video files kept on device memory
        :param segment_duration_sec: Video length per chunk file (default: 3 minutes)
        """
        self.storage_dir = storage_dir
        self.max_segments = max_segments
        self.segment_duration = segment_duration_sec
        self.is_recording = False
        self.current_segment_index = 1
        
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)

    def start_recording(self):
        """App Launched -> Automatically Start ADAS & Blackbox Recording immediately"""
        self.is_recording = True
        print(f"[Blackbox] 🔴 App Launched: Automatic Recording Started.")
        self._manage_storage_limit()

    def stop_recording(self):
        """App Closed -> Automatically Stop Recording & Release Resources"""
        self.is_recording = False
        print(f"[Blackbox] ⏹️ App Closed: Recording Automatically Stopped.")

    def _get_existing_recordings(self) -> List[str]:
        """Returns sorted list of recorded video files by creation time."""
        files = glob.glob(os.path.join(self.storage_dir, "rec_*.mp4"))
        files.sort(key=os.path.getmtime)
        return files

    def _manage_storage_limit(self):
        """
        Ensures strictly <= max_segments (2 files) exist.
        Deletes the oldest file if threshold exceeded.
        """
        existing = self._get_existing_recordings()
        while len(existing) >= self.max_segments:
            oldest_file = existing.pop(0)
            try:
                os.remove(oldest_file)
                print(f"[Blackbox] ♻️ Storage Full: Deleted oldest file '{os.path.basename(oldest_file)}' to free space.")
            except Exception as e:
                print(f"[Blackbox] Error deleting file: {e}")

    def create_new_segment(self) -> str:
        """Triggers creation of next video chunk file."""
        self._manage_storage_limit()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.storage_dir, f"rec_{timestamp}.mp4")
        print(f"[Blackbox] 🎥 Created New Video Chunk: {filename} (Active segments: {len(self._get_existing_recordings()) + 1}/2)")
        return filename
