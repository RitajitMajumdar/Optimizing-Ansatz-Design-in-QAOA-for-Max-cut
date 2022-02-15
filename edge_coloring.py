"""
@author: Ritajit Majumdar

This code is free to download, use and modify as necessary. However, if this code, or its modification
is used for any research publication, or pre-print, please cite arXiv:2106.02812 and arXiv:2110.04637,
or their published versions, if any.
"""


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
        if qc is None or qc.num_qubit != len(self.graph.nodes):
            self.qc = QuantumCircuit(len(self.graph.nodes))
        else:
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
        
        for e in edges:
            opted = False
            colors = col_dict
            for col in colors:
                if e[0] in used[col] or e[1] in used[col]:
                    continue
                else:
                    col_dict[col].append(e)
                    used[col].append(e[0])
                    used[col].append(e[1])
                    opted = True
            if not opted:
                c = c+1
                new_col = 'col'+str(c)
                col_dict[new_col] = []
                col_dict[new_col].append(e)
                used[new_col] = []
                used[new_col].append(e[0])
                used[new_col].append(e[1])
        
        return self._get_parallel_edges(col_dict)
                    
    
    
    
    def ec_ansatz(self,optimize=True,undo_gates=True) -> QuantumCircuit:
        """Returns a p=1 QAOA circuit for Max-Cut with the edge coloring optimization
        Here, we first create the ansatz, and undo everything. In ideal situation, the
        final result should be all zeros. The deviation from the ideal will give an estimate
        of the noise"""
        
        edge_color = self._edge_col()
        
        if not optimize:
            self.qc.h(range(len(self.graph.nodes)))
            for col in list(edge_color.keys()):
                for edge in edge_color[col]:
                    self.qc.cx(edge[0],edge[1])
                    self.qc.rz(self.gamma,edge[1])
                    self.qc.cx(edge[0],edge[1])
            
            if undo_gates:
                self.qc.barrier()
                for col in reversed(list(edge_color.keys())):
                    for edge in edge_color[col]:
                        self.qc.cx(edge[0],edge[1])
                        self.qc.rz(self.gamma,edge[1])
                        self.qc.cx(edge[0],edge[1])
                self.qc.h(range(len(self.graph.nodes)))
            
            self.qc.measure_all()
            
        else:
            first_color = list(edge_color.keys())[0]
            colors = list(edge_color.keys())[1:]
            self.qc.h(range(len(self.graph.nodes)))
            
            for edge in edge_color[first_color]:
                """The first set of edges will not need the 1st CNOT gate"""
                self.qc.rz(self.gamma,edge[1])
                self.qc.cx(edge[0],edge[1])
            
            for col in colors:
                for edge in edge_color[col]:
                    self.qc.cx(edge[0],edge[1])
                    self.qc.rz(self.gamma,edge[1])
                    self.qc.cx(edge[0],edge[1])
        
            # now we undo everything
            if undo_gates:
                self.qc.barrier()
                for col in reversed(colors):
                    for edge in edge_color[col]:
                        self.qc.cx(edge[0],edge[1])
                        self.qc.rz(-1*self.gamma,edge[1])
                        self.qc.cx(edge[0],edge[1])
                
                for edge in edge_color[first_color]:
                    self.qc.cx(edge[0],edge[1])
                    self.qc.rz(-1*self.gamma,edge[1])
            
                self.qc.h(range(len(self.graph.nodes)))
                
            self.qc.measure_all()
        
        return self.qc