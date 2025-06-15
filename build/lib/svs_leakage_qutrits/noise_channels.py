import numpy as np
from qulacs.gate import DenseMatrix, Measurement, X, Y, Z, H, CNOT as CNOT_GATE, SWAP as SWAP_GATE, to_matrix_gate, TwoQubitDepolarizingNoise, CPTP
from .gate_utils import *


# Noise channels and feedback (PMF)
# ================= DEPOLARIZING CHANNELS =================

def QutritQubitDepol(depol_prob, index1, index2, index3):
    """
    Hybrid qutrit-qubit depolarizing channel.
    index1, index2: indices for 2-qubit qutrit encoding (a,b)
    index3: qubit index
    """
    Qub_gates = [
        np.identity(2),
        np.array([[0,1],[1,0]]),
        np.array([[0,-1j],[1j,0]]),
        np.array([[1,0],[0,-1]])
    ]

    Qut_gates = [
        np.identity(4),
        np.array([[0,1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]]),
        np.array([[0,-1j,0,0],[1j,0,0,0],[0,0,1,0],[0,0,0,1]]),
        np.array([[1,0,0,0],[0,-1,0,0],[0,0,1,0],[0,0,0,1]])
    ]

    target_list = [index1, index2, index3]
    gate_list = []
    gate_list.append(DenseMatrix(target_list, np.sqrt(1 - depol_prob) * np.kron(Qub_gates[0], Qut_gates[0])))

    for i in range(4):
        for j in range(4):
            if i == 0 and j == 0:
                continue
            gate_list.append(DenseMatrix(target_list, np.sqrt(depol_prob / 15) * np.kron(Qub_gates[i], Qut_gates[j])))

    return CPTP(gate_list)

def QutritQutritDepol(depol_prob, index1, index2, index3, index4):
    """
    Qutrit-qutrit depolarizing channel.
    index1,index2: first qutrit encoding
    index3,index4: second qutrit encoding
    """
    Qut_gates = [
        np.identity(4),
        np.array([[0,1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]]),
        np.array([[0,-1j,0,0],[1j,0,0,0],[0,0,1,0],[0,0,0,1]]),
        np.array([[1,0,0,0],[0,-1,0,0],[0,0,1,0],[0,0,0,1]])
    ]

    target_list = [index1, index2, index3, index4]
    gate_list = []
    gate_list.append(DenseMatrix(target_list, np.sqrt(1 - depol_prob) * np.kron(Qut_gates[0], Qut_gates[0])))

    for i in range(4):
        for j in range(4):
            if i == 0 and j == 0:
                continue
            gate_list.append(DenseMatrix(target_list, np.sqrt(depol_prob / 15) * np.kron(Qut_gates[i], Qut_gates[j])))

    return CPTP(gate_list)

from scipy.linalg import expm

# ================= PMF (PROJECTIVE FEEDBACK) =================

def feedback_gate(target, G):
    """
    Feedback gate generator for both qubits and encoded qutrits.

    If target is an integer → qubit.
    If target is a tuple (a, b) → encoded qutrit.
    """
    if isinstance(target, int):
        if G == "X":
            return X(target)
        elif G == "Y":
            return Y(target)
        elif G == "Z":
            return Z(target)
        elif G == "H":
            return H(target)
        else:
            raise ValueError(f"Unsupported qubit feedback gate: {G}")

    elif isinstance(target, tuple):
        a, b = target
        if G == "X_01":
            base_gate = controlled_X(a)
            return add_multiple_controls(base_gate, [(b, 0)])
        elif G == "X_02":
            base_gate = controlled_X(b)
            return add_multiple_controls(base_gate, [(a, 0)])
        elif G == "X_12":
            return controlled_SWAP(a, b)
        elif G == "Y_01":
            base_gate = controlled_Y(a)
            return add_multiple_controls(base_gate, [(b, 0)])
        elif G == "Y_02":
            base_gate = controlled_Y(b)
            return add_multiple_controls(base_gate, [(a, 0)])
        elif G == "Z_01":
            base_gate = controlled_Z(a)
            return add_multiple_controls(base_gate, [(b, 0)])
        elif G == "Z_02":
            base_gate = controlled_Z(b)
            return add_multiple_controls(base_gate, [(a, 0)])
        elif G == "H_01":
            base_gate = controlled_H(a)
            return add_multiple_controls(base_gate, [(b, 0)])
        else:
            raise ValueError(f"Unsupported qutrit feedback gate: {G}")

    else:
        raise ValueError("Invalid target type.")

def build_PMF_gate(control, m, G, target):
    measurement_gate = Measurement(control, 0)  # explicit dummy classical register, not used
    feedback = feedback_gate(target, G)
    feedback.add_control_qubit(control, control_value=m)
    return [measurement_gate, feedback]

def build_PMF_gate_qutrit(a, b, m, G, target):
    """
    Builds PMF gate where control is a qutrit (encoded into (a,b)).

    Parameters:
        a, b: physical qubits encoding the qutrit control.
        m: logical measurement outcome (0,1,2).
        G: feedback gate ("X", "Y", "Z", "H")
        target: target qubit for feedback.
    """

    # Apply measurements on both a and b (collapse qutrit)
    meas_a = Measurement(a, 0)
    meas_b = Measurement(b, 1)

    # Decode logical value: 2 * b + a
    # We mimic this by setting multiple classical conditions:
    controls = []
    if m == 0:
        controls = [(a, 0), (b, 0)]
    elif m == 1:
        controls = [(a, 1), (b, 0)]
    elif m == 2:
        controls = [(a, 0), (b, 1)]
    else:
        raise ValueError(f"Invalid logical outcome {m} for qutrit PMF.")

    feedback = feedback_gate(target, G)
    feedback = add_multiple_controls(feedback, controls)

    return [meas_a, meas_b, feedback]

# ================= RESET =======================

def reset_to_zero_cptp(qubit_index):
    K0 = DenseMatrix(qubit_index, np.array([[1, 0], [0, 0]], dtype=np.complex128))
    K1 = DenseMatrix(qubit_index, np.array([[0, 1], [0, 0]], dtype=np.complex128))
    return CPTP([K0, K1])
