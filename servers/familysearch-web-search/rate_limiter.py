"""
Rate limiting utilities for FamilySearch web scraping
"""
import asyncio
import time
from typing import Dict, Optional
from collections import deque
import structlog

logger = structlog.get_logger()

class RateLimiter:
    """Rate limiter for HTTP requests"""
    
    def __init__(self, requests_per_minute: int = 30, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_window = 60  # seconds
        self.hour_window = 3600  # seconds
        
        # Track requests with timestamps
        self.minute_requests = deque()
        self.hour_requests = deque()
        
        # Minimum delay between requests
        self.min_delay = 60.0 / requests_per_minute if requests_per_minute > 0 else 0
        self.last_request_time = 0
    
    async def acquire(self) -> None:
        """Acquire permission to make a request"""
        current_time = time.time()
        
        # Clean up old requests
        self._cleanup_old_requests(current_time)
        
        # Check if we're at the limit
        if len(self.minute_requests) >= self.requests_per_minute:
            wait_time = self.minute_window - (current_time - self.minute_requests[0])
            if wait_time > 0:
                logger.warning("Rate limit exceeded, waiting", wait_time=wait_time)
                await asyncio.sleep(wait_time)
        
        if len(self.hour_requests) >= self.requests_per_hour:
            wait_time = self.hour_window - (current_time - self.hour_requests[0])
            if wait_time > 0:
                logger.warning("Hourly rate limit exceeded, waiting", wait_time=wait_time)
                await asyncio.sleep(wait_time)
        
        # Ensure minimum delay between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        # Record this request
        self.minute_requests.append(current_time)
        self.hour_requests.append(current_time)
        self.last_request_time = current_time
    
    def _cleanup_old_requests(self, current_time: float) -> None:
        """Remove old requests from tracking"""
        # Clean minute requests
        while self.minute_requests and current_time - self.minute_requests[0] >= self.minute_window:
            self.minute_requests.popleft()
        
        # Clean hour requests
        while self.hour_requests and current_time - self.hour_requests[0] >= self.hour_window:
            self.hour_requests.popleft()
    
    def get_stats(self) -> Dict[str, int]:
        """Get current rate limiting statistics"""
        current_time = time.time()
        self._cleanup_old_requests(current_time)
        
        return {
            "minute_requests": len(self.minute_requests),
            "hour_requests": len(self.hour_requests),
            "minute_limit": self.requests_per_minute,
            "hour_limit": self.requests_per_hour
        }

class RetryHandler:
    """Handles retries with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute a function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(
                        "Request failed, retrying",
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        delay=delay,
                        error=str(e)
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("Request failed after all retries", error=str(e))
                    raise last_exception