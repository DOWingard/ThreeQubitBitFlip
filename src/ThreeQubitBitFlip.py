from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator as Aer
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer.noise import NoiseModel, pauli_error
import numpy as np

'''
Derek Wingard,  4/2025

3 qubit bit flip coded 


import the function run_qc() and run to execute

'''

#############################################################################################################

'''Uncomment and run once if you need to set up your IBM account for backend use''' 

#TOKEN = input('paste IBM API Token:  ')
#QiskitRuntimeService.save_account(channel="ibm_quantum", token=TOKEN)

#############################################################################################################


data = QuantumRegister(3, 'data')
ancilla = QuantumRegister(2,'anc')
syndrome = ClassicalRegister(2, 'syndrome')

def bit_flip_operator(qc):
    qc.h(data[0])
    qc.cx(data[0],data[1])
    qc.cx(data[0],data[2])

def entangle_ancillas(qc):
    qc.cx(data[0], ancilla[0])
    qc.cx(data[1], ancilla[0])
    qc.cx(data[1], ancilla[1])
    qc.cx(data[2], ancilla[1]) 

def syndrome_signature_and_correct(qc):
    qc.x(data[0])
    qc.cx(ancilla[0], data[0]) 
    qc.ccx(ancilla[0], ancilla[1], data[0]) 

    qc.x(data[2])
    qc.cx(ancilla[1], data[2])
    qc.ccx(ancilla[0], ancilla[1], data[2])

    qc.ccx(ancilla[0], ancilla[1], data[1])
  
def final_output(qc): 
    output = ClassicalRegister(1)
    qc.add_register(output)    
    qc.measure(data[0],output[0])




#############################################################################################################

def run_qc():
    NOISE = int(input('select noise model (enter 1 for IBM Brisbane noise, enter 2 for 10% bit flip at gates):  '))
    QC = QuantumCircuit(data,ancilla,syndrome)
    bit_flip_operator(QC)
    entangle_ancillas(QC)
    syndrome_signature_and_correct(QC)
    final_output(QC)

    
    if NOISE == 1:
        
        service = QiskitRuntimeService()
        sim = service.backend('ibm_brisbane')
        noise_model = NoiseModel.from_backend(sim)
        sim = Aer()

        transpiled_circuit = transpile(QC,backend=sim, basis_gates=noise_model.basis_gates, coupling_map=sim.configuration().coupling_map)

    if NOISE == 2 :
        
        sim = Aer()
        noise_model = NoiseModel.from_backend(sim)
        bitflip_prob = 0.1  
        bitflip_error = pauli_error([('X', bitflip_prob), ('I', 1 - bitflip_prob)])
        bitflip_error_2q = pauli_error([
            ('II', bitflip_prob), ('IX', 0.5*(1-bitflip_prob)), ('XI', 0.5*(1-bitflip_prob)) 
            ])
        noise_model.add_all_qubit_quantum_error(bitflip_error, ['id', 'x'])
        noise_model.add_all_qubit_quantum_error(bitflip_error_2q, ['cx'])
        transpiled_circuit = transpile(QC,backend=sim)

    elif np.abs(NOISE) > 2 :
        print('NOISE must be 1 or 2')
        exit()

    
    
    job = sim.run(transpiled_circuit, shots=1024)
    result = job.result()
    counts = result.get_counts()
    print("Measurement outcomes:", counts)



