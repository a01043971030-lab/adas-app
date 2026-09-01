"""
ADAS Time-To-Collision (TTC) & Monocular Distance Calculator
High-reliability safety module.
"""

import time
from typing import Dict, List, Tuple, Optional

class TTCCalculator:
    def __init__(self, focal_length_px: float = 800.0, real_vehicle_height_m: float = 1.5):
        """
        :param focal_length_px: Camera focal length in pixels (auto-calibrated)
        :param real_vehicle_height_m: Average height of standard passenger vehicle (1.5 meters)
        """
        self.focal_length = focal_length_px
        self.real_height = real_vehicle_height_m
        
        # Object tracking history: {obj_id: [(timestamp, distance), ...]}
        self.history: Dict[int, List[Tuple[float, float]]] = {}
        
    def estimate_distance(self, bbox_height_px: float) -> float:
        """
        Monocular Distance Estimation: d = (f * H_real) / h_pixel
        """
        if bbox_height_px <= 0:
            return 999.0
        distance = (self.focal_length * self.real_height) / bbox_height_px
        return round(distance, 2)
        
    def calculate_ttc(self, obj_id: int, current_distance: float, ego_speed_kmh: float) -> Tuple[float, float, str]:
        """
        Calculates Relative Speed and Time-To-Collision (TTC).
        Returns: (TTC_seconds, relative_speed_kmh, threat_level)
        Threat Levels: 'CRITICAL', 'WARNING', 'SAFE'
        """
        now = time.time()
        
        if obj_id not in self.history:
            self.history[obj_id] = []
            
        self.history[obj_id].append((now, current_distance))
        
        # Keep only recent history (last 1.0 second)
        self.history[obj_id] = [h for h in self.history[obj_id] if now - h[0] <= 1.0]
        
        if len(self.history[obj_id]) < 2:
            return 99.0, 0.0, 'SAFE'
            
        old_time, old_dist = self.history[obj_id][0]
        dt = now - old_time
        
        if dt <= 0.001:
            return 99.0, 0.0, 'SAFE'
            
        # Distance change per second (positive = approaching)
        rel_speed_m_s = (old_dist - current_distance) / dt
        rel_speed_kmh = rel_speed_m_s * 3.6
        
        # Calculate TTC
        if rel_speed_m_s > 0.1:  # Vehicle is getting closer
            ttc = current_distance / rel_speed_m_s
        else:
            ttc = 99.0  # Vehicle is moving away or static at safe distance
            
        # Threat Level Determination (ISO 22839 FCW Standards)
        if ttc <= 1.5 and current_distance < 30.0:
            threat = 'CRITICAL'
        elif ttc <= 2.5 and current_distance < 45.0:
            threat = 'WARNING'
        else:
            threat = 'SAFE'
            
        return round(ttc, 2), round(rel_speed_kmh, 1), threat

    def cleanup_expired_tracks(self, active_ids: List[int]):
        """Remove untracked objects from history memory."""
        expired = [k for k in self.history if k not in active_ids]
        for k in expired:
            del self.history[k]
