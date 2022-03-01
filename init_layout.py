"""
@author: Ritajit Majumdar

This code is free to download, use and modify as necessary. However, if this code, or its modification
is used for any research publication, or pre-print, please cite arXiv:2106.02812 and arXiv:2110.04637,
or their published versions, if any.
"""


from heuristic import Heuristic
import numpy as np
import networkx as nx
from networkx.classes.graph import Graph

from typing import List, Optional, Union, Tuple
from qiskit.circuit import QuantumCircuit
from qiskit import *


class InitLayout(Heuristic):
    
    def __init__(self,
                graph: Union[Graph, List],
                backend_graph: Union[Graph, List[List], List[Tuple]],
                gamma: float,
                start_vertex: Optional[int] = 0,
                max_bf: Optional[int] = 3,
                qc: Optional[QuantumCircuit] = None,
                seed_transpiler: Optional[int] = 0,
                ):
        super().__init__(graph,gamma,start_vertex=start_vertex,max_bf=max_bf,qc=qc)
        self.seed_transpiler = seed_transpiler
        
        if not isinstance(backend_graph, Graph):
            self.coupling_map = backend_graph
        else:
            self.coupling_map = list(backend_graph.edges)
    
    
    def get_init_layout(self) -> List:
        """Returns the initial layout of the quantum circuit"""
        if self.qc is None:
            qc = super().heuristic_ansatz(undo_gates=False)
        else:
            qc = self.qc.compose(super().heuristic_ansatz(undo_gates=False))
            
        qc = transpile(qc,coupling_map=self.coupling_map,optimization_level=3,seed_transpiler=self.seed_transpiler,basis_gates=['h','cx','x','sx','rz','swap'])
        
        init_layout = {}
        
        for i in range(len(qc._layout)):
            if qc._layout[i].register.name == 'q':
                init_layout[qc._layout[i].index] = i
        
        return list(init_layout.keys())