"""libCacheSim Python bindings"""

from __future__ import annotations

from .libcachesim_python import (
    Cache,
    Request,
    ReqOp,
    ReaderInitParam,
    TraceType,
    SamplerType,
    AnalysisParam,
    AnalysisOption,
    CommonCacheParams,
    __doc__,
    __version__,
)

from .cache import (
    CacheBase,
    # Core algorithms
    LHD,
    LRU,
    FIFO,
    LFU,
    ARC,
    Clock,
    Random,
    # Advanced algorithms
    S3FIFO,
    Sieve,
    LIRS,
    TwoQ,
    SLRU,
    WTinyLFU,
    LeCaR,
    LFUDA,
    ClockPro,
    Cacheus,
    # Optimal algorithms
    Belady,
    BeladySize,
    # Probabilistic algorithms
    LRUProb,
    FlashProb,
    # Size-based algorithms
    Size,
    GDSF,
    # Hyperbolic algorithms
    Hyperbolic,
    # Extra deps
    ThreeLCache,
    GLCache,
    LRB,
    # Plugin cache
    PluginCache,
)

from .trace_reader import TraceReader
from .trace_analyzer import TraceAnalyzer
from .synthetic_reader import SyntheticReader, create_zipf_requests, create_uniform_requests
from .util import Util

__all__ = [
    # Core classes
    "Cache",
    "Request",
    "ReqOp",
    "ReaderInitParam",
    "TraceType",
    "SamplerType",
    "AnalysisParam",
    "AnalysisOption",
    "CommonCacheParams",
    # Cache base class
    "CacheBase",
    # Core cache algorithms
    "LHD",
    "LRU",
    "FIFO",
    "LFU",
    "ARC",
    "Clock",
    "Random",
    # Advanced cache algorithms
    "S3FIFO",
    "Sieve",
    "LIRS",
    "TwoQ",
    "SLRU",
    "WTinyLFU",
    "LeCaR",
    "LFUDA",
    "ClockPro",
    "Cacheus",
    # Optimal algorithms
    "Belady",
    "BeladySize",
    # Probabilistic algorithms
    "LRUProb",
    "FlashProb",
    # Size-based algorithms
    "Size",
    "GDSF",
    # Hyperbolic algorithms
    "Hyperbolic",
    # Extra deps
    "ThreeLCache",
    "GLCache",
    "LRB",
    # Plugin cache
    "PluginCache",
    # Readers and analyzers
    "TraceReader",
    "TraceAnalyzer",
    "SyntheticReader",
    # Trace generators
    "create_zipf_requests",
    "create_uniform_requests",
    # Utilities
    "Util",
    # Metadata
    "__doc__",
    "__version__",
]
