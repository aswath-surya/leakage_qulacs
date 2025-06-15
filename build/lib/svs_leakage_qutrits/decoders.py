from .encoding import EncodingMap

# The following is a majority check decoder, other encoders (ML/MWPM) to be included
def majority_check_decoder(bitstring_list, encoding_map, expected_logical_value=0):
    """
    I will include other decoder options. I need to also make this decoder more general (choice for what is the expected logical ouput needs to be provided)

    Majority-check decoder for encoded qutrits.
    (a, b) encoding map:
        (0,0) -> 0
        (1,0) -> 1
        (0,1) -> 2
        (1,1) -> invalid (raises error)
    """
    n_total = encoding_map.total_physical_qubits()
    n_samples = len(bitstring_list)
    logical_error_count = 0
    leakage_counts = {qt: 0 for qt in encoding_map.qutrits}

    for bitstring in bitstring_list:
        decoded_values = {}

        for qt in encoding_map.qutrits:
            a, b = encoding_map.logical_to_physical(qt)
            bit_a = int(bitstring[n_total - 1 - a])
            bit_b = int(bitstring[n_total - 1 - b])
            # print(a, b, bit_a, bit_b) # Error analysis
            logical = 2 * bit_b + bit_a

            if logical == 3:
                raise ValueError(f"Invalid qutrit state: (a,b) = (1,1) for qutrit {qt}")

            decoded_values[qt] = logical

        values = list(decoded_values.values())
        logical_sum = sum(values)

        logical_value = 1 if logical_sum >= 2 else 0  # majority rule

        if logical_value != expected_logical_value:
            logical_error_count += 1

        for qt, val in decoded_values.items():
            # print(qt, val) # Result analysis
            if val == 2:
                leakage_counts[qt] += 1

    logical_error_rate = logical_error_count / n_samples
    leakage_rates = {qt: leakage_counts[qt] / n_samples for qt in encoding_map.qutrits}
    return logical_error_rate, leakage_rates
