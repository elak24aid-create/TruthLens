import time
from collections import defaultdict
from fastapi import Request, HTTPException, status


class SimpleRateLimiter:
    """
    Sliding-window rate limiter per client IP.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.client_records = defaultdict(list)

    def __call__(self, request: Request):
        # Determine client identifier
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        window_start = current_time - 60.0

        # Filter out timestamps outside current 1-minute window
        timestamps = [t for t in self.client_records[client_ip] if t > window_start]
        self.client_records[client_ip] = timestamps

        if len(timestamps) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute allowed.",
            )

        self.client_records[client_ip].append(current_time)
        return True
