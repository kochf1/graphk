##
## GraphK - Framework for Graph-based execution and pipeline programming.
## core/pipeline.py — Abstractions for composing and structuring executable graphs.
##
# Copyright (c) 2025, Dr. Fernando Koch
#    http://github.com/kochf1/graphk
#
# Disclosure:
# This code was developed through 'vibe coding'. Certain components
# required manual implementation, and human-in-the-loop review and refinement
# were applied throughout the project.
#

import json
from typing import Union, Callable, List, Any, Dict, Iterator, Iterable, Optional, Mapping, Sequence
from .nodes import Node

##
## PIPELINE CLASS
##

class Pipeline(Node):
    """
    Declarative pipeline node.
    """

    def __init__(
        self,
        nodes: Iterable[Node],
        *,
        id: Optional[Any] = None,
    ):
        super().__init__(id=id)
        self._nodes_: List[Node] = list(nodes)
        self._running_: bool = False
        return 
    
    # ---------------------------------------------
    #  Magic Methods
    # ---------------------------------------------

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)
    
    # -------------------------------------------------
    #  Node API 
    # -------------------------------------------------

    def ping(self) -> bool:
        return all(node.ping() for node in self._nodes_)

    def info(self) -> dict:
        data = self.to_dict()
        data["type"] = "pipeline"
        return data

    def step(self):
        raise RuntimeError(
            "Pipeline.step() is not a valid operation."
        )

    # -------------------------------------------------
    #  Execution flags (set by Runner only)
    # -------------------------------------------------

    def start(self) -> None:
        self._running_ = True

    def pause(self) -> None:
        self._running_ = False

    # -------------------------------------------------
    #  Serialization
    # -------------------------------------------------

    def to_dict(self) -> dict:
        data = super().to_dict()
        del data["context"]
        data.update({
            "running": self._running_,
            "nodes": [node.to_dict() for node in self._nodes_],
        })
        return data
