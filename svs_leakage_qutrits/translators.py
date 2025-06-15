import numpy as np
from qulacs.gate import DenseMatrix, Measurement, X, Y, Z, H, CNOT as CNOT_GATE, SWAP as SWAP_GATE, to_matrix_gate, TwoQubitDepolarizingNoise, CPTP
from .encoding import EncodingMap
from .gate_utils import *
from .noise_channels import *
from .leakage_models import *

# ================= GATE TRANSLATOR =================

class GateTranslator:
    """
    Translates parsed gate instructions into Qulacs gates, respecting encoding map.
    """
    def __init__(self, encoding_map, cptp_list=None):
        self.enc = encoding_map
        self.cptp_list = cptp_list if cptp_list is not None else []

    def _validate_kraus(self, kraus_ops, tol=1e-8):
        d = kraus_ops[0].shape[0]
        identity = np.eye(d)
        summation = np.zeros((d, d), dtype=complex)
        for K in kraus_ops:
            if K.shape[0] != K.shape[1]:
                raise ValueError("Kraus operators must be square matrices.")
            if K.shape != kraus_ops[0].shape:
                raise ValueError("Inconsistent dimensions among Kraus operators.")
            summation += K.conj().T @ K
        if not np.allclose(summation, identity, atol=tol):
            raise ValueError("Provided Kraus operators do not satisfy CPTP completeness condition.")

    def translate_gate(self, gate_name, params):
        # Single qubit gates (physical qubits only)
        if gate_name in ["X", "Y", "Z", "H"]:
            target_phys = self.enc.logical_to_physical(params[0])
            if isinstance(target_phys, tuple):
                raise ValueError(f"Cannot apply {gate_name} directly to qutrits")
            gate_dict = {"X": X, "Y": Y, "Z": Z, "H": H}
            return gate_dict[gate_name](target_phys)

        # CNOT (auto-handle hybrid cases)
        if gate_name == "CNOT":
            ctrl, tgt = params
            ctrl_phys = self.enc.logical_to_physical(ctrl)
            tgt_phys  = self.enc.logical_to_physical(tgt)

            # qubit-qubit case
            if not isinstance(ctrl_phys, tuple) and not isinstance(tgt_phys, tuple):
                return CNOT_GATE(ctrl_phys, tgt_phys)

            # qubit -> qutrit
            if not isinstance(ctrl_phys, tuple) and isinstance(tgt_phys, tuple):
                a_tgt, b_tgt = tgt_phys
                base_gate = controlled_X(a_tgt)
                return add_multiple_controls(base_gate, [(ctrl_phys, 1), (b_tgt, 0)])

            # qutrit -> qubit
            if isinstance(ctrl_phys, tuple) and not isinstance(tgt_phys, tuple):
                a_ctrl, b_ctrl = ctrl_phys
                base_gate = controlled_X(tgt_phys)
                return add_multiple_controls(base_gate, [(a_ctrl, 0), (tgt_phys, 1)])

            # qutrit -> qutrit
            if isinstance(ctrl_phys, tuple) and isinstance(tgt_phys, tuple):
                a_ctrl, b_ctrl = ctrl_phys
                a_tgt,  b_tgt  = tgt_phys
                base_gate = controlled_X(a_tgt)
                return add_multiple_controls(base_gate, [(a_ctrl, 1), (b_ctrl, 0), (b_tgt, 0)])

        # SWAP (only qubit-qubit swap currently)
        if gate_name == "SWAP" and all(not isinstance(self.enc.logical_to_physical(p), tuple) for p in params):
            t1_phys = self.enc.logical_to_physical(params[0])
            t2_phys = self.enc.logical_to_physical(params[1])
            return SWAP_GATE(t1_phys, t2_phys)

        # Qutrit-specific gates
        if gate_name.startswith("X_01"):
            a, b = self.enc.logical_to_physical(params[0])
            base_gate = controlled_X(a)
            return add_multiple_controls(base_gate, [(b,0)])

        elif gate_name.startswith("X_02"):
            a, b = self.enc.logical_to_physical(params[0])
            base_gate = controlled_X(b)
            return add_multiple_controls(base_gate, [(a,0)])

        elif gate_name.startswith("X_12"):
            a, b = self.enc.logical_to_physical(params[0])
            return controlled_SWAP(a, b)

        elif gate_name.startswith("Y_01"):
            a, b = self.enc.logical_to_physical(params[0])
            base_gate = controlled_Y(a)
            return add_multiple_controls(base_gate, [(b,0)])

        elif gate_name.startswith("Y_02"):
            a, b = self.enc.logical_to_physical(params[0])
            base_gate = controlled_Y(b)
            return add_multiple_controls(base_gate, [(a,0)])

        elif gate_name.startswith("Z_01"):
            a, b = self.enc.logical_to_physical(params[0])
            base_gate = controlled_Z(a)
            return add_multiple_controls(base_gate, [(b,0)])

        elif gate_name.startswith("Z_02"):
            a, b = self.enc.logical_to_physical(params[0])
            base_gate = controlled_Z(b)
            return add_multiple_controls(base_gate, [(a,0)])

        elif gate_name.startswith("H_01"):
            a, b = self.enc.logical_to_physical(params[0])
            base_gate = controlled_H(a)
            return add_multiple_controls(base_gate, [(b, 0)])

        # PMF
        elif gate_name == "PMF":
            ctrl, m, G, target = params
            ctrl_phys = self.enc.logical_to_physical(ctrl)
            target_phys = self.enc.logical_to_physical(target)

            if isinstance(target_phys, tuple):
                raise ValueError("PMF target must be a physical qubit")

            if isinstance(ctrl_phys, tuple):
                # qutrit control case
                a, b = ctrl_phys
                return build_PMF_gate_qutrit(a, b, m, G, target_phys)
            else:
                # qubit control case
                return build_PMF_gate(ctrl_phys, m, G, target_phys)

        # Measurement
        elif gate_name == "M":
            target = params[0]
            target_phys = self.enc.logical_to_physical(target)
            if isinstance(target_phys, tuple):
                a, b = target_phys
                return [Measurement(a, 0), Measurement(b, 0)]
            else:
                return Measurement(target_phys, 0)

        # DEPOL handling (core addition!)
        elif gate_name == "DEPOL":
            idx1, idx2, prob = params
            phys1 = self.enc.logical_to_physical(idx1)
            phys2 = self.enc.logical_to_physical(idx2)

            # both are qubits
            if not isinstance(phys1, tuple) and not isinstance(phys2, tuple):
                return TwoQubitDepolarizingNoise(phys1, phys2, prob)

            # qutrit-qubit hybrid
            if isinstance(phys1, tuple) and not isinstance(phys2, tuple):
                a, b = phys1
                return QutritQubitDepol(prob, a, b, phys2)

            if not isinstance(phys1, tuple) and isinstance(phys2, tuple):
                a, b = phys2
                return QutritQubitDepol(prob, a, b, phys1)

            # qutrit-qutrit
            if isinstance(phys1, tuple) and isinstance(phys2, tuple):
                a1, b1 = phys1
                a2, b2 = phys2
                return QutritQutritDepol(prob, a1, b1, a2, b2)

        elif gate_name == "LEAK":
            qutrit_index, model_type, decay_prob = params
            if qutrit_index not in self.enc.qutrits:
                raise ValueError(f"LEAK applied to non-qutrit index {qutrit_index}")
            a, b = self.enc.logical_to_physical(qutrit_index)
            return LeakageChannel(decay_prob, a, b, model_type)

        elif gate_name.startswith("CPTP"):
            cptp_idx, logical_targets = params

            # Verify CPTP list length
            if cptp_idx >= len(self.cptp_list):
                raise IndexError(f"CPTP index {cptp_idx} exceeds provided CPTP list.")

            # Map logical indices to physical qubits
            physical_targets = []
            for log_idx in logical_targets:
                phys = self.enc.logical_to_physical(log_idx)
                if isinstance(phys, tuple):
                    physical_targets.extend(phys)
                else:
                    physical_targets.append(phys)

            kraus_ops = self.cptp_list[cptp_idx]

            self._validate_kraus(kraus_ops)

            gate_list = []
            for K in kraus_ops:
                gate = DenseMatrix(physical_targets, K)
                gate_list.append(gate)

            return CPTP(gate_list)

        elif gate_name == "RESET":
            target_list = params  # list of logical indices
            gates = []
            for logical_target in target_list:
                phys = self.enc.logical_to_physical(logical_target)
                if isinstance(phys, tuple):
                    # apply reset on both physical qubits encoding the qutrit
                    for p in phys:
                        gates.append(reset_to_zero_cptp(p))
                else:
                    gates.append(reset_to_zero_cptp(phys))
            return gates

        else:
            raise ValueError(f"Unknown gate type: {gate_name}")
