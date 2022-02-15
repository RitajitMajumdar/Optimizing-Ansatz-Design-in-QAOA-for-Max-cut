"""
@author: Ritajit Majumdar

This code is free to download, use and modify as necessary. However, if this code, or its modification
is used for any research publication, or pre-print, please cite arXiv:2106.02812 and arXiv:2110.04637,
or their published versions, if any.
"""

from edge_coloring import EdgeColoring
from circuit import Circuit

import numpy as np
import networkx as nx
from networkx.classes.graph import Graph

from typing import List, Optional, Union
from qiskit.circuit import QuantumCircuit
from qiskit import *


class DFS(EdgeColoring):
    
    def __init__(self,
                graph: Union[Graph, List],
                gamma: float,
                start_vertex: int,
                qc: Optional[QuantumCircuit] = None,
                ):
        super().__init__(graph,gamma,qc)
        self.start_vertex = start_vertex
    
    
    def _get_opt_edges(self) -> List:
        """Returns the list of edges along the DFS tree"""
        visited = []
        to_opt = []
        
        for edges in list(nx.dfs_edges(self.graph,self.start_vertex)):
            if edges[0] not in visited and edges[1] not in visited:
                to_opt.append(edges)
                visited.append(edges[0])
                visited.append(edges[1])
            if edges[0] in visited and edges[1] not in visited:
                to_opt.append(edges)
                visited.append(edges[1])
        
        return to_opt
    
    
    def dfs_ansatz(self,optimize=True,undo_gates=True) -> QuantumCircuit:
        """Returns a p=1 QAOA circuit for Max-Cut with the depth first search optimization
        Here, we first create the ansatz, and undo everything. In ideal situation, the
        final result should be all zeros. The deviation from the ideal will give an estimate
        of the noise"""
        
        if not optimize:
            return super().ec_ansatz(optimize=optimize,undo_gates=undo_gates)
        
        else:
            opt_edges = self._get_opt_edges()
            no_opt_edges = []
            
            for edge in self.graph.edges:
                if (edge[0],edge[1]) not in opt_edges and (edge[1],edge[0]) not in opt_edges:
                    no_opt_edges.append(edge)
            
            no_opt_order = super()._edge_col(no_opt_edges)
            
            circ = Circuit(opt_edges,no_opt_order,self.gamma)
            
            if self.qc is None:
                self.qc = circ.create_circuit(optimize=optimize,undo_gates=undo_gates)
            else:
                try:
                    self.qc = self.qc.compose(circ.create_circuit(optimize=optimize,undo_gates=undo_gates))
                except:
                    raise ValueError("Could not compose the circuit with the provided circuit!")
            
            return self.qc