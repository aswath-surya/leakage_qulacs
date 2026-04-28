Leakage Circuit Compiler (README)
===============================

Some aspects currently deprecated. Will be updated soon.
---

The Leakage Circuit Compiler is a Python package for simulating hybrid qubit-qutrit quantum circuits that include leakage, noise, and arbitrary CPTP channels. It is built on top of the qulacs simulator, and supports a flexible circuit string format that allows the specification of encoding, gates, noise models, and measurements.

Circuit String Input Format:

The input string specifies the circuit in two parts: (1) the encoding map and (2) the gate list.

1. Encoding Declaration (first line)

QT <qutrit_indices> Q <qubit_indices>;

- QT: logical qutrit indices (each encoded into 2 qubits).
- Q: logical qubit indices.
- The total number of physical qubits equals total_qubits + 2 * total_qutrits.
- If only qubits or only qutrits are present, either declaration may be omitted.

Example:
QT 2 3 Q 0 1 4;

2. Gate List (subsequent lines, separated by semicolons)

The following gates and noise channels are supported:

- Single-qubit gates:
  X <index>;
  Y <index>;
  Z <index>;
  H <index>;

- Encoded single-qutrit gates:
  X_01 <qutrit_index>;
  X_02 <qutrit_index>;
  X_12 <qutrit_index>;
  Y_01 <qutrit_index>;
  Y_02 <qutrit_index>;
  Z_01 <qutrit_index>;
  Z_02 <qutrit_index>;

- Two-qubit/qutrit gates:
  CNOT <control> <target>;
  SWAP <index1> <index2>;

- Depolarizing channels:
  DEPOL <index1> <index2> <probability>;

Depolarizing channels support all hybrid combinations: qubit-qubit, qubit-qutrit, and qutrit-qutrit. The depolarizing channels are properly constructed to act on encoded qutrits.

- Leakage models:
  LEAK I <qutrit_index> <probability>;
  LEAK C <qutrit_index> <probability>;

Both incoherent (Kraus map) and coherent (Hamiltonian-based unitary) leakage channels are supported for qutrit indices.

- Projective Measurement Feedback (PMF):
  PMF <control> <outcome> <gate> <target>;

PMF supports both qubit and encoded qutrit control qubits. Feedback gates can act on qubits or qutrits depending on the context.

- Reset channels:
  RESET <index1> <index2> ... <indexN>;

Resets physical qubits to |0⟩ state.

- Arbitrary CPTP channels via Kraus operators:
  CPTPi <cptp_list_index> <target_indices...>;

The user may supply Kraus operator lists at runtime and reference them by index through CPTPi. Kraus operators are verified internally to ensure they satisfy the completeness condition Σ K†K = I.

- Measurements:
  M <index>;

3. Separator

Each gate instruction must terminate with a semicolon (;).

Simulation Modes

The simulator supports both:

- internal mode: Qulacs native CPTP sampling (samples one Kraus operator per shot deterministically)
- external mode: explicit Monte Carlo sampling (samples fresh Kraus operators per gate per shot)

The simulation mode is selected when creating the SimulatorRunner object by setting mode="internal" or mode="external".

Decoders

Currently, a majority-check decoder is implemented. For encoded qutrits (a, b):

(0,0) → logical 0
(1,0) → logical 1
(0,1) → logical 2
(1,1) → invalid (raises error)

The decoder uses majority vote across all qutrits to determine the final logical value. The decoder can be configured to check against an expected logical value during simulation.

Requirements

The following Python packages are required:

qulacs
numpy
scipy

License

Default license: MIT.

