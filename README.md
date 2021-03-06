# Optimizing Ansatz Design in QAOA for Max-cut
This repository contains codes for finding the p = 1 QAOA ansatz for Max-Cut using Edge Coloring Method, Depth First Search Method and the Heuristic Cost Function Method. The file circuit.py creates the circuit given the list of optimized and other edges. On the other hand, edge_coloring.py, dfs.py and heuristic.py creates the list of optimized edges based on their correspoding methods.

Requirements: Python3 and Qiskit are required to run this code. The used Qiskit version is 0.17.4. However, it should work with other versions of Qiskit as well.

This research is a collaboration between Indian Statistical Institute, and IBM India Research Lab. The collaborators are Dhiraj Madan, Debasmita Bhoumik, Dhinakaran Vinayagamurthy, Shesha Raghunathan and Susmita Sur-Kolay. The corresponding papers can be found in https://arxiv.org/abs/2106.02812 and https://arxiv.org/abs/2110.04637.
