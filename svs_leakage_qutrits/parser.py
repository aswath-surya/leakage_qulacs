# ================= PARSER =================
def parse_circuit_string(circuit_str):
    """
    Parse circuit string into qutrit list, qubit list, and gate list.
    """
    lines = [line.strip() for line in circuit_str.split(";") if line.strip()]
    header = lines[0]
    header_parts = header.split()

        # Initialize
    qutrits = []
    qubits = []

    # Parse qutrits
    if "QT" in header_parts:
        qt_index = header_parts.index("QT")
        # Look for Q after QT (if present), else read to end
        q_index = header_parts.index("Q") if "Q" in header_parts else len(header_parts)
        qutrits = list(map(int, header_parts[qt_index+1:q_index]))

    # Parse qubits
    if "Q" in header_parts:
        q_index = header_parts.index("Q")
        qubits = list(map(int, header_parts[q_index+1:]))

    # qt_index = header_parts.index("QT")
    # q_index  = header_parts.index("Q")
    # qutrits = list(map(int, header_parts[qt_index+1:q_index]))
    # qubits  = list(map(int, header_parts[q_index+1:]))

    gates = []
    for line in lines[1:]:
        parts = line.split()
        gate_name = parts[0]
        if gate_name == "PMF":
            ctrl = int(parts[1])
            m = int(parts[2])
            G = parts[3]
            target = int(parts[4])
            params = [ctrl, m, G, target]
        elif gate_name == "DEPOL":
            idx1 = int(parts[1])
            idx2 = int(parts[2])
            prob = float(parts[3])
            params = [idx1, idx2, prob]
        elif gate_name == "LEAK":
            model_flag = parts[1].upper()
            leak_model = "incoherent" if model_flag == "I" else "coherent" if model_flag == "C" else None
            if leak_model is None:
                raise ValueError(f"Unknown LEAK model: {model_flag}")
            qutrit_index = int(parts[2])
            decay_prob = float(parts[3])
            params = [qutrit_index, leak_model, decay_prob]
        elif gate_name.startswith("CPTP"):
            idx = int(gate_name[4:])  # extracts integer i from "CPTPi"
            targets = list(map(int, parts[1:]))
            params = [idx, targets]
        elif gate_name == "RESET":
            targets = list(map(int, parts[1:]))
            params = targets
        else:
            params = list(map(int, parts[1:]))
        gates.append((gate_name, params))

    return qutrits, qubits, gates
