from qulacs import QuantumCircuit, QuantumState
from .encoding import EncodingMap
from .parser import parse_circuit_string
from .translators import GateTranslator

class SimulatorRunner:
    """
    Master simulator interface: internal and external sampling.
    """
    def __init__(self, circuit_string, cptp_list=[], mode="external", shots=1024, expected_logical_value=0):
        self.qutrits, self.qubits, self.gates = parse_circuit_string(circuit_string)
        self.encoding = EncodingMap(self.qutrits, self.qubits)
        self.translator = GateTranslator(self.encoding, cptp_list)
        self.num_qubits = self.encoding.total_physical_qubits()
        self.mode = mode
        self.shots = shots

    def build_circuit(self):
        circuit = QuantumCircuit(self.num_qubits)
        for gate_name, params in self.gates:
            gate = self.translator.translate_gate(gate_name, params)
            if isinstance(gate, list):
                for g in gate:
                    circuit.add_gate(g)
            else:
                circuit.add_gate(gate)
        return circuit

    def run_internal(self):
        circuit = self.build_circuit()
        bitstrings = []
        for _ in range(self.shots):
            state = QuantumState(self.num_qubits)
            circuit.update_quantum_state(state)
            sample = state.sampling(1)[0]
            bitstring = format(sample, f"0{self.num_qubits}b")
            bitstrings.append(bitstring)
        return bitstrings

    def run_external(self):
        bitstrings = []
        for _ in range(self.shots):
            circuit = self.build_circuit()  # fresh CPTP samples each time
            state = QuantumState(self.num_qubits)
            circuit.update_quantum_state(state)
            sample = state.sampling(1)[0]
            bitstring = format(sample, f"0{self.num_qubits}b")
            bitstrings.append(bitstring)
        return bitstrings

    def run_and_decode(self, decode_mode="majority", expected_logical_value=0):
        """
        Full simulation + decoding pipeline.

        decode_mode: "majority" (only option for now).
        """
        if self.mode == "internal":
            bitstrings = self.run_internal()
        elif self.mode == "external":
            bitstrings = self.run_external()
        else:
            raise ValueError("Unknown simulation mode.")

        if decode_mode == "majority":
            return majority_check_decoder(bitstrings, self.encoding, expected_logical_value)
        else:
            raise ValueError("Unknown decoder.")
