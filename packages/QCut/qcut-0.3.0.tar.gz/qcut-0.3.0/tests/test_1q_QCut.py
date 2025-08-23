"""Tests for CircuitKnitting package."""  # noqa: N999

import numpy as np
from qiskit_aer import AerSimulator

#import QCut as ck
import QCut.single_qubit_wirecut as wc
import tests.solutions_1q as sq
from QCut.wirecut import _remove_obsm


def test_get_cut_locations() -> None:
    """Test get_cut_locations function.

    This function tests whether the get_cut_location method correctly identifies
    the cut locations in the provided test circuits by comparing the result to
    the pre-defined solutions.
    """
    for solution_index, circ in enumerate(sq.test_circuits):
        print(solution_index)
        assert np.array_equal(
            wc._get_cut_locations(circ.copy()),
            sq.cut_location_solutions[solution_index],
        )


def test_separate_subcircuits() -> None:
    """Test separate_subcircuits function.

    This function tests whether the get_locations_and_subcircuits method correctly
    identifies the locations and separates the subcircuits for each test circuit
    by comparing the operations in the generated subcircuits to the pre-defined
    solutions.
    """
    count = 0
    for solution_index, circ in enumerate(sq.test_circuits):
        qss, circs, map_qubits = wc.get_locations_and_subcircuits(circ.copy())
        _remove_obsm(circs)
        print(count)
        count += 1
        for circ_index, subcirc in enumerate(circs):
            for op1, op2 in zip(
                subcirc.data, sq.subcircuit_solutions[solution_index][circ_index]
            ):
                assert op1.operation.name == op2.operation.name  # noqa: S101


# def test_get_experiment_circuits() -> None:
#     """Test get_experiment_circuits function.

#     This function tests whether the get_experiment_circuits method correctly
#     generates the experiment circuits from the subcircuits and qubit subsets for
#     each test circuit by comparing the operations in the generated experiment
#     circuits to the pre-defined solutions.
#     """
#     for solution_index, circ in enumerate(sq.test_circuits):
#         # Retrieve qubit locations and subcircuits
#         qss, circuits = wc.get_locations_and_subcircuits(circ)

#         # Generate experiment circuits
#         experiment_circuits, coefs, id_meas = ck.get_experiment_circuits(circuits, 
#                                                                           qss)

#         assert np.array_equal(coefs, s.coefs_solutions[solution_index])

#         assert np.array_equal(id_meas, s.id_meas_solutions[solution_index])
#         # Flatten the nested list of experiment circuits and extract their data
#         test_data = [
#             op.data for sublist in experiment_circuits.circuits for op in sublist
#         ]

#         # Retrieve the corresponding solution data
#         solution_data = s.experiment_circuit_solutions[solution_index]

#         # Validate the operations
#         for test_ops, solution_ops in zip(test_data, solution_data):
#             for test_op, solution_op in zip(test_ops, solution_ops):
#                 assert test_op.operation.name == solution_op.operation.name, (
#                     f"Operation mismatch: {test_op.operation.name} != "
#                     f"{solution_op.operation.name}"
#                 )


def test_expectation_values() -> None:
    """Test the expectation values of the test circuits.

    This function tests whether the run method correctly calculates the expectation
    values for each test circuit and its corresponding observable by comparing the
    results to the pre-defined solutions within a specified error tolerance.

    The test runs each circuit on the AerSimulator backend without error mitigation.
    """
    # Initialize the simulator
    sim = AerSimulator()

    # Iterate over each test circuit and its corresponding expected solutions
    for solution_index, circ in enumerate(sq.test_circuits):
        print(solution_index)
        # Calculate expectation values using the run method
        expvals = wc.run(
            circ, sq.test_observables[solution_index], backend=sim
        )
        # Check each calculated expectation value against the corresponding
        # expected value
        tolerance = 0.1
        print(expvals)
        print(sq.exp_val_solutions[solution_index])
        for check in [
            abs(a - b) <= tolerance
            for a, b in zip(expvals, sq.exp_val_solutions[solution_index])
        ]:
            assert check  # noqa: S101
