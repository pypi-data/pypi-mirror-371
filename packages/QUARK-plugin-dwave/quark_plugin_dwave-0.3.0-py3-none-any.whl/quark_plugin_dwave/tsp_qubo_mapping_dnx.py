import logging
from dataclasses import dataclass
from typing import override

import dwave_networkx as dnx

from quark.core import Core, Data, Result
from quark.interface_types import Graph, Other, Qubo
from quark_plugin_tsp import TspQuboMapping


@dataclass
class TspQuboMappingDnx(TspQuboMapping):
    """A module for mapping a graph to a QUBO formalism for the TSP problem."""

    @override
    def preprocess(self, data: Graph) -> Result:
        self._graph = data.as_nx_graph()
        q = dnx.traveling_salesperson_qubo(self._graph)
        return Data(Qubo.from_dnx_qubo(q, len(data.as_adjacency_matrix())))
