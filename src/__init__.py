"""
GraphK - Framework for Graph-based execution and pipeline programming.
"""

from importlib.metadata import version
from .core.nodes import Gate, Node, BranchNode
from .core.pipeline import Pipeline
from .core.runner import Runner, Session
from .core.emitter import Emitter

__all__ = [
    "Gate", 
    "Node",
    "BranchNode",
    "Pipeline",
    "Runner",
    "Session",
    "Emitter"
]

__title__ = "graphk"
__description__ = "Framework for Graph-based execution and pipeline programming"
__github__ = "https://github.com/kochf1/graphk"
__license__ = "MIT"
__about__ = """
GraphK provides the core execution model for graph-based programming. It defines 
pipelines as executable graphs composed of nodes, branches, and nested pipelines, 
with explicit control flow and runtime semantics. GraphK is UI-agnostic and 
domain-independent, serving as the foundation on which all other GraphK modules 
and products are built.
"""

try: __version__ = version(__title__)
except: __version__ = "0.0.0"


