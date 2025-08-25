# This code is part of cqlib.
#
# Copyright (C) 2025 China Telecom Quantum Group.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Gates module for defining custom quantum gates and their equivalence rules.

This module provides custom quantum gates (e.g., X2P, X2M, Y2P, Y2M, XY2P, XY2M)
and their equivalence rules with standard Qiskit gates. It also includes
validation to ensure the correctness of the gate definitions.
"""

from math import pi

import numpy as np
from cqlib.circuits.gates.rxy import RXY
from cqlib.circuits.gates.x import X2P, X2M
from cqlib.circuits.gates.xy import XY2P, XY2M
from cqlib.circuits.gates.y import Y2P, Y2M
from qiskit.circuit import Gate, QuantumCircuit, Parameter
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as SELib
from qiskit.circuit.library import GlobalPhaseGate, RXGate, RYGate, \
    HGate, XGate, YGate


class X2PGate(Gate):
    """
    Custom quantum gate representing a positive X rotation by π/2.

    This gate is equivalent to a rotation around the X-axis by π/2 radians.
    """

    def __init__(self, label=None):
        """
        Initializes the X2PGate.

        Args:
            label (str, optional): A custom label for the gate. Defaults to None.
        """
        super().__init__("x2p", 1, params=[], label=label)

    def _define(self):
        """Defines the quantum circuit for the X2P gate."""
        defn = QuantumCircuit(1)
        defn.rx(pi / 2, 0)
        self._definition = defn

    def __array__(self, dtype=None, copy=None):
        """
        Returns the matrix representation of the gate.

        Args:
            dtype: The data type of the array.
            copy: Whether to avoid copying the array.

        Returns:
            np.ndarray: The matrix representation of the gate.

        Raises:
            ValueError: If copying cannot be avoided.
        """
        if copy is False:
            raise ValueError("unable to avoid copy while creating an array as requested")
        return np.asarray(X2P(), dtype=dtype)


class X2MGate(Gate):
    """
    Custom quantum gate representing a negative X rotation by π/2.

    This gate is equivalent to a rotation around the X-axis by -π/2 radians.
    """

    def __init__(self, label=None):
        """
        Initializes the X2MGate.

        Args:
            label (str, optional): A custom label for the gate. Defaults to None.
        """
        super().__init__("x2m", 1, [], label=label)

    def _define(self):
        """Defines the quantum circuit for the X2M gate."""
        defn = QuantumCircuit(1)
        defn.rx(-pi / 2, 0)
        self._definition = defn

    def __array__(self, dtype=None, copy=None):
        """
        Returns the matrix representation of the gate.

        Args:
            dtype: The data type of the array.
            copy: Whether to avoid copying the array.

        Returns:
            np.ndarray: The matrix representation of the gate.

        Raises:
            ValueError: If copying cannot be avoided.
        """
        if copy is False:
            raise ValueError("unable to avoid copy while creating an array as requested")
        return np.asarray(X2M(), dtype=dtype)


class Y2PGate(Gate):
    """
    Custom quantum gate representing a positive Y rotation by π/2.

    This gate is equivalent to a rotation around the Y-axis by π/2 radians.
    """

    def __init__(self, label=None):
        """
        Initializes the Y2PGate.

        Args:
            label (str, optional): A custom label for the gate. Defaults to None.
        """
        super().__init__("y2p", 1, params=[], label=label)

    def _define(self):
        """Defines the quantum circuit for the Y2P gate."""
        defn = QuantumCircuit(1)
        defn.ry(pi / 2, 0)
        self._definition = defn

    def __array__(self, dtype=None, copy=None):
        """
        Returns the matrix representation of the gate.

        Args:
            dtype: The data type of the array.
            copy: Whether to avoid copying the array.

        Returns:
            np.ndarray: The matrix representation of the gate.

        Raises:
            ValueError: If copying cannot be avoided.
        """
        if copy is False:
            raise ValueError("unable to avoid copy while creating an array as requested")
        return np.asarray(Y2P(), dtype=dtype)


class Y2MGate(Gate):
    """
    Custom quantum gate representing a negative Y rotation by π/2.

    This gate is equivalent to a rotation around the Y-axis by -π/2 radians.
    """

    def __init__(self, label=None):
        """
        Initializes the Y2MGate.

        Args:
            label (str, optional): A custom label for the gate. Defaults to None.
        """
        super().__init__("y2m", 1, [], label=label)

    def _define(self):
        """Defines the quantum circuit for the Y2M gate."""
        defn = QuantumCircuit(1)
        defn.ry(-pi / 2, 0)
        self._definition = defn

    def __array__(self, dtype=None, copy=None):
        """
        Returns the matrix representation of the gate.

        Args:
            dtype: The data type of the array.
            copy: Whether to avoid copying the array.

        Returns:
            np.ndarray: The matrix representation of the gate.

        Raises:
            ValueError: If copying cannot be avoided.
        """
        if copy is False:
            raise ValueError("unable to avoid copy while creating an array as requested")
        return np.asarray(Y2M(), dtype=dtype)


class XY2PGate(Gate):
    """
    Custom quantum gate representing a positive XY rotation.

    This gate is parameterized by an angle `theta` and represents a rotation
    in the XY plane.
    """

    def __init__(self, theta: float | Parameter, label: str = None):
        """
        Initializes the XY2PGate.

        Args:
            theta (float|Parameter): The rotation angle.
            label (str, optional): A custom label for the gate. Defaults to None.
        """
        super().__init__("xy2p", 1, [theta], label=label)

    def _define(self):
        """Defines the quantum circuit for the XY2P gate."""
        theta_ = self.params[0]
        defn = QuantumCircuit(1)
        defn.rz(pi / 2 - theta_, 0)
        defn.ry(pi / 2, 0)
        defn.rz(theta_ - pi / 2, 0)
        self._definition = defn

    def __array__(self, dtype=None, copy=None):
        """
        Returns the matrix representation of the gate.

        Args:
            dtype: The data type of the array.
            copy: Whether to avoid copying the array.

        Returns:
            np.ndarray: The matrix representation of the gate.

        Raises:
            ValueError: If copying cannot be avoided.
        """
        if copy is False:
            raise ValueError("unable to avoid copy while creating an array as requested")
        return np.asarray(XY2P(self.params[0]), dtype=dtype)


class XY2MGate(Gate):
    """
    Custom quantum gate representing a negative XY rotation.

    This gate is parameterized by an angle `theta` and represents a rotation
    in the XY plane.
    """

    def __init__(self, theta: float | Parameter, label: str = None):
        """
        Initializes the XY2MGate.

        Args:
            theta (float | Parameter): The rotation angle.
            label (str, optional): A custom label for the gate. Defaults to None.
        """
        super().__init__("xy2m", 1, [theta], label=label)

    def _define(self):
        """Defines the quantum circuit for the XY2M gate."""
        theta_ = self.params[0]
        defn = QuantumCircuit(1)
        defn.rz(-pi / 2 - theta_, 0)
        defn.ry(pi / 2, 0)
        defn.rz(theta_ + pi / 2, 0)
        self._definition = defn

    def __array__(self, dtype=None, copy=None):
        """
        Returns the matrix representation of the gate.

        Args:
            dtype: The data type of the array.
            copy: Whether to avoid copying the array.

        Returns:
            np.ndarray: The matrix representation of the gate.

        Raises:
            ValueError: If copying cannot be avoided.
        """
        if copy is False:
            raise ValueError("unable to avoid copy while creating an array as requested")
        return np.asarray(XY2M(self.params[0]), dtype=dtype)


class RxyGate(Gate):
    """A parameterized two-axis rotation gate in the XY plane.

    This gate implements a composite rotation consisting of Rz and Rx operations.
    The rotation is parameterized by two angles (phi and theta) which control
    the Z-axis rotations before and after the X-axis π/2 rotations.

    Args:
        phi (float | Parameter): Rotation angle (in radians) for initial Z-axis rotation.
            Controls the phase offset in the composite rotation sequence.
        theta (float | Parameter): Rotation angle (in radians) for middle Z-axis rotation.
            Determines the main rotation magnitude between X-axis operations.
        label (str, optional): Optional text label for gate identification. Defaults to None.

    Example:
        >>> import math
       >>> from qiskit import QuantumCircuit
        >>> qc = QuantumCircuit(1)
        >>> qc.append(RxyGate(math.pi/3, math.pi/4), [0])
    """

    def __init__(self, phi: float | Parameter, theta: float | Parameter, label: str = None):
        """
        Initializes the RxyGate.

        Args:
            phi (float | Parameter): The rotation angle.
            theta (float | Parameter): The rotation angle.
            label (str, optional): A custom label for the gate. Defaults to None.
        """
        super().__init__("rxy", 1, [phi, theta], label=label)

    def _define(self):
        """Defines the quantum circuit for the RXY gate.

        Implements gate using rotation sequence:
        Rz(π/2 - φ) → Rx(π/2) → Rz(θ) → Rx(-π/2) → Rz(φ - π/2)
        """
        phi_ = Parameter("phi")
        theta_ = Parameter("theta")
        defn = QuantumCircuit(1)
        defn.rz(pi / 2 - phi_, 0)
        defn.rx(pi / 2, 0)
        defn.rz(theta_, 0)
        defn.rx(-pi / 2, 0)
        defn.rz(phi_ - pi / 2, 0)
        self._definition = defn

    def __array__(self, dtype=None, copy=None):
        """
        Returns the matrix representation of the gate.

        Args:
            dtype: The data type of the array.
            copy: Whether to avoid copying the array.

        Returns:
            np.ndarray: The matrix representation of the gate.

        Raises:
            ValueError: If copying cannot be avoided.
        """
        if copy is False:
            raise ValueError("unable to avoid copy while creating an array as requested")
        return np.asarray(RXY(self.params[0], self.params[1]), dtype=dtype)


x_qc = QuantumCircuit(1)
x_qc.rx(pi / 2, 0)
SELib.add_equivalence(X2PGate(), x_qc)

# x
x_qc = QuantumCircuit(1)
x_qc.append(X2PGate(), [0])
x_qc.append(X2PGate(), [0])
x_qc.append(GlobalPhaseGate(pi / 2), [])
SELib.add_equivalence(XGate(), x_qc)

# RX
t_ = Parameter("theta")
rx_qc = QuantumCircuit(1)
rx_qc.rz(pi / 2, 0)
rx_qc.append(X2PGate(), [0])
rx_qc.rz(t_, 0)
rx_qc.append(X2MGate(), [0])
rx_qc.rz(-pi / 2, 0)
SELib.add_equivalence(RXGate(t_), rx_qc)

# RY
t_ = Parameter("theta")
ry_qc = QuantumCircuit(1)
ry_qc.append(X2PGate(), [0])
ry_qc.rz(t_, 0)
ry_qc.append(X2MGate(), [0])
SELib.add_equivalence(RYGate(t_), ry_qc)

# X2M
x2m_qc = QuantumCircuit(1)
x2m_qc.rx(-pi / 2, 0)
SELib.add_equivalence(X2MGate(), x2m_qc)

ry_qc = QuantumCircuit(1)
ry_qc.ry(pi / 2, 0)
SELib.add_equivalence(Y2PGate(), ry_qc)

# Y
y_qc = QuantumCircuit(1)
y_qc.append(Y2PGate(), [0])
y_qc.append(Y2PGate(), [0])
y_qc.append(GlobalPhaseGate(pi / 2), [])
SELib.add_equivalence(YGate(), y_qc)

ry_qc = QuantumCircuit(1)
ry_qc.ry(-pi / 2, 0)
SELib.add_equivalence(Y2MGate(), ry_qc)

#  H gate
h_decomp = QuantumCircuit(1)
h_decomp.rz(pi, 0)
h_decomp.append(Y2PGate(), [0])
h_decomp.append(GlobalPhaseGate(pi / 2), [])
SELib.add_equivalence(HGate(), h_decomp)

# XY2P
t_ = Parameter("theta")
xy2p_qc = QuantumCircuit(1)
xy2p_qc.rz(pi / 2 - t_, 0)
xy2p_qc.ry(pi / 2, 0)
xy2p_qc.rz(t_ - pi / 2, 0)
SELib.add_equivalence(XY2PGate(t_), xy2p_qc)

# XY2M
t_ = Parameter("theta")
xy2m_qc = QuantumCircuit(1)
xy2m_qc.rz(-pi / 2 - t_, 0)
xy2m_qc.ry(pi / 2, 0)
xy2m_qc.rz(t_ + pi / 2, 0)
SELib.add_equivalence(XY2MGate(t_), xy2m_qc)

p_ = Parameter("phi")
t_ = Parameter("theta")
qc = QuantumCircuit(1)
qc.rz(pi / 2 - p_, 0)
qc.rx(pi / 2, 0)
qc.rz(t_, 0)
qc.rx(-pi / 2, 0)
qc.rz(p_ - pi / 2, 0)
SELib.add_equivalence(RxyGate(p_, t_), qc)

__all__ = [
    'X2PGate',
    'X2MGate',
    'Y2PGate',
    'Y2MGate',
    'XY2PGate',
    'XY2MGate',
    'RxyGate'
]
