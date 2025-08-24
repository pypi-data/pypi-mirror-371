"""
Triyak React Performance Suite - Python Bindings
The world's most advanced React performance optimization toolkit

Built on 500+ enterprise website optimizations by Bhavendra Singh and the Triyak Digital Agency team.

Author: Bhavendra Singh
Company: Triyak Digital Agency
Website: https://www.triyak.in
Email: info@triyak.in
LinkedIn: https://www.linkedin.com/in/bhavendra-singh
"""

__version__ = "1.0.0"
__author__ = "Bhavendra Singh"
__company__ = "Triyak Digital Agency"
__website__ = "https://www.triyak.in"
__email__ = "info@triyak.in"
__linkedin__ = "https://www.linkedin.com/in/bhavendra-singh"

# Import main classes
from .performance_suite import TriyakPerformanceSuite
from .performance_monitor import TriyakPerformanceMonitor
from .core_web_vitals import CoreWebVitalsOptimizer
from .bundle_optimizer import BundleOptimizer
from .memory_optimizer import MemoryOptimizer
from .ai_optimizer import AIOptimizer

__all__ = [
    "TriyakPerformanceSuite",
    "TriyakPerformanceMonitor", 
    "CoreWebVitalsOptimizer",
    "BundleOptimizer",
    "MemoryOptimizer",
    "AIOptimizer",
]

# Package information
PACKAGE_INFO = {
    "name": "triyak-react-performance",
    "version": __version__,
    "description": "The world's most advanced React performance optimization toolkit",
    "author": __author__,
    "company": __company__,
    "website": __website__,
    "email": __email__,
    "linkedin": __linkedin__,
    "features": [
        "Core Web Vitals optimization",
        "AI-powered performance tuning", 
        "Bundle optimization",
        "Memory management",
        "Real-time monitoring",
        "Enterprise features"
    ],
    "performance_improvements": "300-500%",
    "core_web_vitals_score": "95+",
    "enterprise_clients": "500+",
    "years_experience": "10+"
}
