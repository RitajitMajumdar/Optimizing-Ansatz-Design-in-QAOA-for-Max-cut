"""
@author: Ritajit Majumdar

This code is free to download, use and modify as necessary. However, if this code, or its modification
is used for any research publication, or pre-print, please cite arXiv:2106.02812 and arXiv:2110.04637,
or their published versions, if any.
"""


from typing import Optional, List
from qiskit import QuantumCircuit
import networkx as nx


class Circuit():
    
    def __init__(self,
                opt_edges: List,
                no_opt_edges: dict,
                gamma: float,
                ):
        
        self.opt_edges = opt_edges
        self.no_opt_edges = no_opt_edges
        self.gamma = gamma
        self.graph = nx.Graph()
        edges = self.opt_edges
        for color, edge_list in self.no_opt_edges.items():
            edges = edges + edge_list
        self.graph.add_edges_from(edges)
        self.qc = QuantumCircuit(len(self.graph.nodes))
            
        
    def _add_unoptimized_edges(self, undo_gates:bool):
        """Appends the circuit corresponding to the unoptimized edges"""
        
        for color in list(self.no_opt_edges.keys()):
            for edge in self.no_opt_edges[color]:
                self.qc.cx(edge[0],edge[1])
                self.qc.rz(self.gamma,edge[1])
                self.qc.cx(edge[0],edge[1])
        
        if undo_gates:
            self.qc.barrier()
            
            for color in reversed(list(self.no_opt_edges.keys())):
                for edge in self.no_opt_edges[color]:
                    self.qc.cx(edge[0],edge[1])
                    self.qc.rz(-1*self.gamma,edge[1])
                    self.qc.cx(edge[0],edge[1])
    
        
    def create_circuit(self,optimize=True,undo_gates=True) -> QuantumCircuit:
        """Given the set of optimized and unoptimized edges, creates the quantum circuit"""
        self.qc.h(range(self.qc.num_qubits))
        
        if not optimize:
            for edge in self.opt_edges:
                self.qc.cx(edge[0],edge[1])
                self.qc.rz(self.gamma,edge[1])
                self.qc.cx(edge[0],edge[1])
        
        else:
            for edge in self.opt_edges:
                self.qc.rz(self.gamma,edge[1])
                self.qc.cx(edge[0],edge[1])
        
        self._add_unoptimized_edges(undo_gates=undo_gates)
        
        if undo_gates:
            if not optimize:
                for edge in reversed(self.opt_edges):
                    self.qc.cx(edge[0],edge[1])
                    self.qc.rz(-1*self.gamma,edge[1])
                    self.qc.cx(edge[0],edge[1])
            else:
                for edge in reversed(self.opt_edges):
                    self.qc.cx(edge[0],edge[1])
                    self.qc.rz(-1*self.gamma,edge[1])
            
            self.qc.h(range(self.qc.num_qubits))
        
        self.qc.measure_all()
        
        return self.qc