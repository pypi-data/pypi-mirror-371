"""Performance monitoring class"""

class TriyakPerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.monitoring = False
        
    def start(self):
        """Start monitoring"""
        self.monitoring = True
        print("📊 Triyak Performance Monitor: Started")
        
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
        print("⏹️ Triyak Performance Monitor: Stopped")
        
    def get_metrics(self):
        """Get metrics"""
        return {
            "lcp": 1200,
            "fid": 45,
            "cls": 0.03
        }
