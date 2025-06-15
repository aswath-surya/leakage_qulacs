# ================= ENCODING =================
class EncodingMap:
    """
    Manages mapping of logical indices to physical qubits, handling qutrit-to-qubit encoding.
    """
    def __init__(self, qutrits, qubits):
        self.qutrits = qutrits
        self.qubits = qubits
        self.total_qutrits = len(qutrits)
        self.total_qubits = len(qubits)
        self.offset = self.total_qutrits + self.total_qubits
        self.encoding = {}
        # for qt in qutrits:
        #     self.encoding[qt] = (qt, qt + self.offset)
        # for qb in qubits:
        #     self.encoding[qb] = qb
        phys_idx = 0

        for qt in qutrits:
            self.encoding[qt] = (phys_idx, phys_idx+1)
            phys_idx += 2

        for qb in qubits:
            self.encoding[qb] = phys_idx
            phys_idx += 1

    def logical_to_physical(self, logical_index):
        return self.encoding[logical_index]

    def total_physical_qubits(self):
        return self.total_qubits + 2*self.total_qutrits
