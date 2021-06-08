# Optimizing-Ansatz-Design-in-QAOA-for-Max-cut
The repository contains the code to find the probability of error for the traditional QAOA ansatz, and the proposed Edge coloring and Depth First Search Based Ansatz. This code was written in the IBM Quantum Lab (https://quantum-computing.ibm.com/lab). Therefore, some of the imports are strictly the IBM Quantum Lab requirements. In order to run it in local device, one needs to install a local version of Qiskit, and may require to add or remove a few imports.

This particular code uses the Manhattan Noise Model (noise_model_FakeManhattan.pkl). The same code can be executed for any other noise model. The corresponding file must be provided for such a case. Finally, it is not necessary to use a .pkl file for the noise model. One may choose to use a .json file (or some other file format) as well. In such cases, the code must be properly modified with the necessary parser.

Requirements: In order to run this code, one requires Python3 and Qiskit. The used Qiskit version is 0.17.4. However, it should work with other versions of Qiskit as well.

This research is a collaboration between Indian Statistical Institute, and IBM India Research Lab. The collaborators are Ritajit Majumdar, Dhiraj Madan, Debasmita Bhoumik, Dhinakaran Vinayagamurthy, Shesha Raghunathan and Susmita Sur-Kolay. The corresponding paper can be found in https://arxiv.org/abs/2106.02812
