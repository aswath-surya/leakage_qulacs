import numpy as np
from scipy.linalg import expm
from qulacs.gate import DenseMatrix, CPTP, DiagonalMatrix

def LeakageChannel(decay_prob, index1, index2, model_type="incoherent"):
    """
    General leakage channel acting on encoded qutrit (index1, index2).

    Parameters:
        decay_prob (float): leakage probability
        index1, index2 (int): physical qubit indices representing qutrit
        model_type (str): leakage model ("incoherent" or "coherent")
    """
    if model_type == "incoherent":
        # Kraus operators for incoherent leakage
        L1 = np.zeros((4, 4))
        L1[2, 1] = np.sqrt(decay_prob)
        diag_elements = np.array([1, np.sqrt(1 - decay_prob), 1, 1])
        diagonal_gate = DiagonalMatrix([index1, index2], diag_elements)
        L1_gate = DenseMatrix([index1, index2], L1)
        return CPTP([diagonal_gate, L1_gate])

    elif model_type == "coherent":
        SWAP_operator = np.array([
            [1,0,0,0],
            [0,0,1,0],
            [0,1,0,0],
            [0,0,0,1]
        ])
        theta = np.sqrt(decay_prob)
        U_leak = expm(1j * theta * SWAP_operator)
        return DenseMatrix([index1, index2], U_leak)

    else:
        raise ValueError(f"Unsupported leakage model: {model_type}")
