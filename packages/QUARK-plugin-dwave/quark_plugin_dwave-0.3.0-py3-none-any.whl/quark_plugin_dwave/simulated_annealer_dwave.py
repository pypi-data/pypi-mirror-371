from dataclasses import dataclass
from typing import override

import dwave.samplers

from quark.core import Core, Data, Result
from quark.interface_types import Other, Qubo


@dataclass
class SimulatedAnnealerDwave(Core):
    """
    A module for solving a qubo problem using simulated annealing

    :param num_reads: The number of reads to perform
    """

    num_reads: int = 100

    @override
    def preprocess(self, data: Qubo) -> Result:
        device = dwave.samplers.SimulatedAnnealingSampler()
        q = data.as_dnx_qubo()
        self._result = device.sample_qubo(q, num_reads=self.num_reads)
        return Data(None)

    @override
    def postprocess(self, data: Data) -> Result:
        solution_list = []
        for key in sorted(self._result.lowest().first.sample.keys()):
            solution_list.append(self._result.lowest().first.sample[key])
        return Data(Other(solution_list))  # type: ignore
