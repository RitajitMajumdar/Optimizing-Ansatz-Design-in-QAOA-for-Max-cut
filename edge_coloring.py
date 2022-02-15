"""
@author: Ritajit Majumdar

This code is free to download, use and modify as necessary. However, if this code, or its modification
is used for any research publication, or pre-print, please cite arXiv:2106.02812 and arXiv:2110.04637,
or their published versions, if any.
"""

from circuit import Circuit

import numpy as np
import networkx as nx
from networkx.classes.graph import Graph

from typing import List, Optional, Union
from qiskit.circuit import QuantumCircuit
from qiskit import *

class EdgeColoring():
    
    def __init__(self,
                graph: Union[Graph, List],
                gamma: float,
                qc: Optional[QuantumCircuit] = None,
                ):
        
        if isinstance(graph, Graph):
            self.graph = graph
        else:
            G = nx.Graph()
            G.add_edges_from(graph)
            self.graph = G
        
        self.gamma = gamma
        self.qc = qc
    
    
    def _get_parallel_edges(self, col_dict: dict) -> dict:
        """Returns the sorted color dictionary"""
        sorted_col_dict = {}
        len_edges = 0
        first_color = list(col_dict.keys())[0]
        
        for color, edges in col_dict.items():
            if len(edges) > len_edges:
                len_edges = len(edges)
                first_color = color
        
        sorted_col_dict[first_color] = col_dict[first_color]
        
        for color, edges in col_dict.items():
            if color != first_color:
                sorted_col_dict[color] = edges
        
        return sorted_col_dict
    
    
    def _edge_col(self, edges: Optional[List] = None) -> dict:
        """Given the list of edges, returns a dictionary {color:edge}"""
        if edges is None:
            edges = list(self.graph.edges)
        
        col_dict = {}
        used = {}
        
        c = 1
        col_dict["col"+str(c)] = []
        used["col"+str(c)] = []
        
        for edge in edges:
            placed = False
            for color in col_dict.keys():
                if edge[0] in used[color] or edge[1] in used[color]:
                    continue
                else:
                    col_dict[color].append(edge)
                    used[color].append(edge[0])
                    used[color].append(edge[1])
                    placed = True
                    break
            if not placed:
                c = c+1
                new_col = 'col'+str(c)
                col_dict[new_col] = [edge]
                used[new_col] = [edge[0],edge[1]]
        
        return self._get_parallel_edges(col_dict)
    
    
    
    def ec_ansatz(self,optimize=True,undo_gates=True) -> QuantumCircuit:
        """Returns a p=1 QAOA circuit for Max-Cut with the edge coloring optimization
        Here, we first create the ansatz, and undo everything. In ideal situation, the
        final result should be all zeros. The deviation from the ideal will give an estimate
        of the noise"""
        
        edge_color = self._edge_col()
        first_color = list(edge_color.keys())[0]
        opt_edges = edge_color[first_color]
        
        del edge_color[first_color]
        
        circ = Circuit(opt_edges,edge_color,self.gamma)
        
        if self.qc is None:
            self.qc = circ.create_circuit(optimize=optimize,undo_gates=undo_gates)
        else:
            try:
                self.qc = self.qc.compose(circ.create_circuit(optimize=optimize,undo_gates=undo_gates))
            except:
                raise ValueError("Could not compose the circuit with the provided circuit!")
        
        return self.qc
        