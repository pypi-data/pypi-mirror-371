"""Test Pauli Frame."""

from surfq.pauli import Pauli


def test_single_pauli_operations():
    """Test Single-Qubit Pauli operations."""
    assert Pauli.I * Pauli.I == Pauli.I
    assert Pauli.X * Pauli.I == Pauli.X
    assert Pauli.Z * Pauli.I == Pauli.Z
    assert Pauli.Y * Pauli.I == Pauli.Y
    assert Pauli.I * Pauli.X == Pauli.X
    assert Pauli.X * Pauli.X == Pauli.I
    assert Pauli.Z * Pauli.X == Pauli.Y
    assert Pauli.Y * Pauli.X == Pauli.Z
    assert Pauli.I * Pauli.Z == Pauli.Z
    assert Pauli.X * Pauli.Z == Pauli.Y
    assert Pauli.Z * Pauli.Z == Pauli.I
    assert Pauli.Y * Pauli.Z == Pauli.X
    assert Pauli.I * Pauli.Y == Pauli.Y
    assert Pauli.X * Pauli.Y == Pauli.Z
    assert Pauli.Z * Pauli.Y == Pauli.X
    assert Pauli.Y * Pauli.Y == Pauli.I
