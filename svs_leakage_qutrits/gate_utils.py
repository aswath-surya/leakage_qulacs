from qulacs.gate import DenseMatrix, Measurement, X, Y, Z, H, CNOT as CNOT_GATE, SWAP as SWAP_GATE, to_matrix_gate, TwoQubitDepolarizingNoise, CPTP

# ================= CONTROLLED GATE UTILS =================
def add_multiple_controls(base_gate, controls):
    for control_index, control_value in controls:
        base_gate.add_control_qubit(control_index, control_value)
    return base_gate

def controlled_X(target):
    return to_matrix_gate(X(target))

def controlled_Y(target):
    return to_matrix_gate(Y(target))

def controlled_Z(target):
    return to_matrix_gate(Z(target))

def controlled_H(target):
    return to_matrix_gate(H(target))

def controlled_SWAP(target1, target2):
    return to_matrix_gate(SWAP_GATE(target1, target2))
