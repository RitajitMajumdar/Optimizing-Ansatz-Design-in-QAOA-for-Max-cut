"""
@author: Ritajit Majumdar

This code is free to download, use and modify as necessary. However, if this code, or its modification
is used for any research publication, or pre-print, please cite arXiv:2106.02812 and arXiv:2110.04637,
or their published versions, if any.
"""


from heuristic import Heuristic
from init_layout import InitLayout

import numpy as np
import networkx as nx
from networkx.classes.graph import Graph

from typing import List, Optional, Union, Tuple
from qiskit.circuit import QuantumCircuit
from qiskit import *


class HardwareHeuristic(Heuristic):
    
    def __init__(self,
                graph: Union[Graph, List],
                backend_graph: Union[Graph, List[List], List[Tuple]],
                gamma: float,
                eta: Optional[int] = 0,
                start_vertex: Optional[int] = 0,
                max_bf: Optional[int] = 3,
                qc: Optional[QuantumCircuit] = None,
                hardware_dist: Optional[dict] = None,
                seed_transpiler: Optional[int] = 0,
                ):
        super().__init__(graph,gamma,start_vertex=start_vertex,max_bf=max_bf,qc=qc)
        
        if not isinstance(backend_graph, Graph):
            self.backend_graph = nx.Graph()
            self.backend_graph.add_edges_from(backend_graph)
            self.coupling_map = backend_graph
        else:
            self.backend_graph = backend_graph
            self.coupling_map = list(backend_graph.edges)
        
        self.seed_transpiler = seed_transpiler
        
        self.max_bf = [self.backend_graph.degree[i] for i in range(len(self.backend_graph.nodes))]
        self.eta = eta
        
        if hardware_dist is None:
            self.hardware_dist = dict(nx.all_pairs_shortest_path_length(self.backend_graph))
        else:
            self.hardware_dist = hardware_dist
        
        # get the initial layout
        init_layout = InitLayout(graph,backend_graph,gamma,start_vertex=start_vertex,max_bf=max_bf,qc=qc,seed_transpiler=seed_transpiler)
        self.init_layout = init_layout.get_init_layout()
    
    
    def eta(self, value: int):
        self.eta = value
    
    
    def _get_best_edge(self, edge_list: List) -> Tuple:
        """Given a set of new edges to choose from, it determines the edge that maximizes the cost function"""
        best_edge = edge_list[0]
        dist = self.hardware_dist[self.init_layout[best_edge[0]]][self.init_layout[best_edge[1]]]
        max_cost = (len(self.graph.nodes) - self.level[best_edge[0]])*(self.max_bf[best_edge[0]] - self.bf[best_edge[0]]) - self.eta*(dist-1)
        
        for edge in edge_list[1:]:
            dist = self.hardware_dist[self.init_layout[edge[0]]][self.init_layout[edge[1]]]
            cost = (len(self.graph.nodes) - self.level[edge[0]])*(self.max_bf[edge[0]] - self.bf[edge[0]]) - self.eta*(dist-1)
            
            if cost > max_cost:
                max_cost = cost
                best_edge = edge
        
        return best_edge
    
    
    def hardware_ansatz(self,optimize=True,undo_gates=True) -> QuantumCircuit:
        """Returns a p=1 QAOA circuit for Max-Cut with the heuristic cost function optimization based on hardware information
        Here, we first create the ansatz, and undo everything. In ideal situation, the
        final result should be all zeros. The deviation from the ideal will give an estimate
        of the noise"""
        
        return super().heuristic_ansatz(optimize=optimize,undo_gates=undo_gates)