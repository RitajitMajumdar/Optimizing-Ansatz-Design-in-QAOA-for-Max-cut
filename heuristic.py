"""
@author: Ritajit Majumdar

This code is free to download, use and modify as necessary. However, if this code, or its modification
is used for any research publication, or pre-print, please cite arXiv:2106.02812 and arXiv:2110.04637,
or their published versions, if any.
"""
from abc import ABC, abstractmethod
from dfs import DFS

import numpy as np
import networkx as nx
from networkx.classes.graph import Graph

from typing import List, Optional, Union, Tuple
from qiskit.circuit import QuantumCircuit
from qiskit import *


class Heuristic(DFS):
    
    def __init__(self,
                graph: Union[Graph, List],
                gamma: float,
                start_vertex: Optional[int] = 0,
                max_bf: Optional[int] = 3,
                qc: Optional[QuantumCircuit] = None,
                ):
        super().__init__(graph,gamma,start_vertex,qc) # this code assumes a connected graph, will not work for disconnected graphs
        self.max_bf = max_bf
        self.level = np.zeros(len(self.graph.nodes),dtype=int)
        self.level[self.start_vertex] = 1
        self.bf = np.zeros(len(self.graph.nodes),dtype=int)
        self.visited = [self.start_vertex]
        self.opt_edges = []
        self.hardware_dist = None
    
    
    def _get_hardware_best_edge(self,edge_list) -> Tuple:
        pass
    
    
    def _get_best_edge(self, edge_list: List) -> Tuple:
        """Given a set of new edges to choose from, it determines the edge that maximizes the cost function"""
        if self.hardware_dist is not None:
            best_edge = self._get_hardware_best_edge(edge_list)
        else:
            best_edge = edge_list[0]
            max_cost = (len(self.graph.nodes) - self.level[best_edge[0]])*(self.max_bf - self.bf[best_edge[0]])
            
            for edge in edge_list[1:]:
                cost = (len(self.graph.nodes) - self.level[edge[0]])*(self.max_bf - self.bf[edge[0]])
                if cost > max_cost:
                    max_cost = cost
                    best_edge = edge
        
        return best_edge
        
    
    def _add_new_node(self):
        """Given a parent node to expand, it finds the best new node to add to the spanning tree such that
        the cost function is maximized"""
        
        new_edge_list = []
        for node in self.visited:
            for child in self.graph.neighbors(node):
                if child not in self.visited:
                    edge = (node,child)
                    new_edge_list.append(edge)
        
        edge_to_add = self._get_best_edge(new_edge_list)
        self.opt_edges.append(edge_to_add)
        self.bf[edge_to_add[0]] = self.bf[edge_to_add[0]]+1
        self.level[edge_to_add[1]] = self.level[edge_to_add[0]] + 1
        self.visited.append(edge_to_add[1])
        
    
    def _get_opt_edges(self):
        """Create the list of optimal edges"""
        while len(self.visited) < len(self.graph.nodes):
            self._add_new_node()
        
        return self.opt_edges
    
    
    def heuristic_ansatz(self,optimize=True,undo_gates=True) -> QuantumCircuit:
        """Returns a p=1 QAOA circuit for Max-Cut with the heuristic cost function optimization
        Here, we first create the ansatz, and undo everything. In ideal situation, the
        final result should be all zeros. The deviation from the ideal will give an estimate
        of the noise"""
        
        return super().dfs_ansatz(optimize=optimize,undo_gates=undo_gates)