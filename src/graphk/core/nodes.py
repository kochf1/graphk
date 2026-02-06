##
## GraphK - Framework for Graph-based execution and pipeline programming.
## core/nodes.py — Primitive abstractions for executable graph computation.
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
import random
from abc import ABC, abstractmethod
from typing import Union, Callable, List, Any, Dict, Iterator, Iterable, Optional, Mapping, Sequence

Checker = Callable[[Any], bool]

##
## GATE CLASS
##

class Gate:
    """
    Basic validation structure.
    """
    # Strategy Constants
    ALL_MATCH = 1      # Logical AND
    ANY_MATCH = 2      # Logical OR
    NONE_MATCH = 3     # Logical NOT (OR)

    def __init__(
        self,
        checkers: Union[Checker, Iterable[Checker]],
        strategy: int = ALL_MATCH,
        *,
        id: Optional[str] = None
    ):
        if id is not None: self.id = id
        self.checkers: List[Checker] = (
            list(checkers) if isinstance(checkers, (list, tuple)) else [checkers]
        )
        self.strategy: int = strategy
        return

    # ---------------------------------------------
    #  Magic Methods
    # ---------------------------------------------

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)
    
    # ---------------------------------------------
    #  Common Interfaces
    # ---------------------------------------------

    def assess(self, context: Optional[Mapping[str, Any]]) -> bool:
        """
        Executes the assessment logic against the provided context (dict)
        """
        # Convert checkers into a generator of booleans
        result = (func(context) for func in self.checkers)

        if self.strategy == self.ALL_MATCH:
            result = all(result)
        
        elif self.strategy == self.ANY_MATCH:
            result =  any(result)
        
        elif self.strategy == self.NONE_MATCH:
            result = not any(result)
        
        else:
            result = False
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Gate",
            "strategy": self.strategy,
            "checkers": [
                getattr(c, "id", repr(c)) for c in self.checkers
            ],
        }
    
##
## NODE CLASS
##

class Node(ABC):
    """
    Base Node.
    """

    def __init__(
        self,
        context: Optional[Mapping[str, Any]] = None,
        *,
        id: Optional[str] = None,
        condition: Optional[Gate] = None,
        validation: Optional[Gate] = None,
        weight: Optional[int] = None,
        next: Optional[Any] = None,
        **kwargs: Any,
    ):
        # Save context
        self.context = context

        # Load Node attributes if they are provided
        if id is not None: self.id = id
        if condition is not None: self.condition = condition
        if validation is not None: self.validation = validation
        if weight is not None: self.weight = weight
        if next is not None: self.next = next
        
        # Load Node configurations
        self.__dict__.update(kwargs)
        return

    # ---------------------------------------------
    #  Magic Methods
    # ---------------------------------------------

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)
    
    # ---------------------------------------------
    #  Common Interfaces
    # ---------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        data = {"type": self.__class__.__name__, "context": self.context}
        for k in ("id", "weight", "condition", "validation"):
            if (v := getattr(self, k, None)) is not None:
                data[k] = v.to_dict() if hasattr(v, "to_dict") else v
        if (n := getattr(self, "next", None)) is not None:
            data["next"] = n.id if hasattr(n, "id") else n.__class__.__name__
        return data
    
    # ---------------------------------------------
    #  Abstract Methods
    # ---------------------------------------------

    @abstractmethod
    def ping(self) -> bool:
        """Health check / Connectivity test."""
        pass

    @abstractmethod
    def info(self) -> dict:
        """Metadata and capability reporting."""
        pass

    @abstractmethod
    def step(self) -> Iterator[Any]:
        """Execution logic; must return iterator."""
        pass


##
## BRANCH NODE CLASS
##

class BranchNode(Node, ABC):
    """
    Branched nodes.
    """

    # Selection strategies
    SELECT_FIRST = 0
    SELECT_RANDOM = 1
    SELECT_BEST = 2

    def __init__(
        self,
        nodes: Sequence[Node],
        strategy: int = SELECT_FIRST,
        *,
        id: Optional[Any] = None,
    ):
        super().__init__(id=id)
        self._nodes_ = nodes
        self._strategy_ = strategy
        return 

    # -------------------------------------------------
    #  Node API 
    # -------------------------------------------------

    def ping(self) -> bool:
        return all(node.ping() for node in self._nodes_)

    def info(self) -> dict:
        data = self.to_dict()
        data["type"] = "branch"
        return data

    def step(self):
        raise RuntimeError(
            "BranchNode.step() is not a valid operation."
        )
    
    # ---------------------------------------------
    #  Common Interfaces
    # ---------------------------------------------

    def select(self) -> Optional[Node]:
        """
        Filters nodes based on their _condition_ Gate and applies the selection strategy.
        """
        selected_node = None

        # 1. Filter valid nodes using the _condition_ gate
        valid_nodes = []
        for node in self._nodes_:
            # If a gate exists, we assess it; otherwise, the path is open (default True)
            is_valid = True
            condition: Optional[Gate] = getattr(node, '_condition_', None)
            if condition is not None:
                is_valid = condition.assess(node.context())
            
            if is_valid:
                valid_nodes.append(node)

        # Fail fast: No valid paths available
        if not valid_nodes:
            return None

        # 2. Apply Selection Strategy
        if self._strategy_ == self.SELECT_FIRST:
            selected_node = valid_nodes[0]

        elif self._strategy_ == self.SELECT_RANDOM:
            selected_node = random.choice(valid_nodes)

        elif self._strategy_ == self.SELECT_BEST:
            # Selection based on the _weight_ attribute
            selected_node = max(valid_nodes, key=lambda n: getattr(n, '_weight_', 0))

        return selected_node
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        del data["context"]
        data.update({
            "strategy": self._strategy_,
            "nodes": [n.to_dict() for n in self._nodes_],
        })
        return data
    


