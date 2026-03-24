# utils/performance.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Performance Monitor
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional
from collections import deque
from functools import wraps

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor performa sistem"""
    
    def __init__(self, slow_threshold: float = 5.0):
        self.slow_threshold = slow_threshold
        self.start_time = time.time()
        self.response_times: List[float] = []
        self.slow_operations: List[Dict] = []
        self.operation_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}
        self.history: deque = deque(maxlen=1000)
    
    def record_response_time(self, duration: float, operation: str = "unknown"):
        self.response_times.append(duration)
        self.operation_counts[operation] = self.operation_counts.get(operation, 0) + 1
        
        if duration > self.slow_threshold:
            self.slow_operations.append({
                'timestamp': time.time(),
                'operation': operation,
                'duration': duration
            })
            if len(self.slow_operations) > 100:
                self.slow_operations = self.slow_operations[-100:]
        
        self._update_metrics()
    
    def record_error(self, error_type: str, operation: str = "unknown"):
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def record_command_usage(self, command: str):
        self.operation_counts[command] = self.operation_counts.get(command, 0) + 1
    
    def _update_metrics(self):
        pass
    
    def get_stats(self) -> Dict:
        uptime = time.time() - self.start_time
        
        if self.response_times:
            avg = sum(self.response_times) / len(self.response_times)
            p95_index = int(len(self.response_times) * 0.95)
            sorted_times = sorted(self.response_times)
            p95 = sorted_times[p95_index] if p95_index < len(sorted_times) else 0
        else:
            avg = 0
            p95 = 0
        
        return {
            'uptime': uptime,
            'total_operations': sum(self.operation_counts.values()),
            'total_errors': sum(self.error_counts.values()),
            'response_time': {'avg': round(avg, 2), 'p95': round(p95, 2)},
            'operation_counts': self.operation_counts,
            'error_counts': self.error_counts,
            'slow_operations': self.slow_operations[-5:]
        }


_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def measure_time(operation: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                op_name = operation or func.__name__
                get_performance_monitor().record_response_time(duration, op_name)
                return result
            except Exception as e:
                duration = time.time() - start
                op_name = operation or func.__name__
                get_performance_monitor().record_error(type(e).__name__, op_name)
                raise
        return wrapper
    return decorator


def async_measure_time(operation: str = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                op_name = operation or func.__name__
                get_performance_monitor().record_response_time(duration, op_name)
                return result
            except Exception as e:
                duration = time.time() - start
                op_name = operation or func.__name__
                get_performance_monitor().record_error(type(e).__name__, op_name)
                raise
        return wrapper
    return decorator


__all__ = [
    'PerformanceMonitor',
    'get_performance_monitor',
    'measure_time',
    'async_measure_time'
]
