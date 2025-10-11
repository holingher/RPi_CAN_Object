import pygame
import time
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

class SwipeDetector:
    def __init__(self):
        self.is_swiping = False
        self.start_pos = None
        self.start_time = None
        self.min_swipe_distance = 100  # Minimum distance for a swipe
        self.max_swipe_time = 0.5  # Maximum time for a swipe (seconds)
        self.last_swipe_time = 0  # To prevent rapid consecutive swipes
        self.swipe_cooldown = 0.5  # Cooldown between swipes (seconds)
        
    def handle_event(self, event):
        """
        Handle pygame events and detect swipe gestures.
        Returns: 'left' for swipe left, 'right' for swipe right, None for no swipe
        """
        current_time = time.time()
        
        # Check if we're still in cooldown period
        if current_time - self.last_swipe_time < self.swipe_cooldown:
            return None
            
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self.is_swiping = True
                self.start_pos = event.pos
                self.start_time = current_time
                
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1 and self.is_swiping:  # Left mouse button
                self.is_swiping = False
                if self.start_pos is not None:
                    end_pos = event.pos
                    end_time = current_time
                    
                    # Calculate swipe distance and time
                    dx = end_pos[0] - self.start_pos[0]
                    dy = end_pos[1] - self.start_pos[1]
                    distance = abs(dx)
                    swipe_time = end_time - self.start_time
                    
                    # Check if it's a valid swipe (horizontal, fast enough, long enough)
                    if (distance >= self.min_swipe_distance and 
                        swipe_time <= self.max_swipe_time and
                        abs(dy) < distance * 0.5):  # More horizontal than vertical
                        
                        self.last_swipe_time = current_time
                        
                        if dx > 0:
                            return 'right'
                        else:
                            return 'left'
                
                self.start_pos = None
                self.start_time = None
                
        elif event.type == MOUSEMOTION and not self.is_swiping:
            # Reset if mouse moves without being pressed
            self.start_pos = None
            self.start_time = None
            
        return None
    
    def reset(self):
        """Reset the swipe detector state"""
        self.is_swiping = False
        self.start_pos = None
        self.start_time = None

# Global swipe detector instance
swipe_detector = SwipeDetector()