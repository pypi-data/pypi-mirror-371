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
TianYan Backend module for managing quantum computing backends.

This module provides classes to handle backend configurations, properties, and operations
for both quantum computers and simulators on the TianYan platform.
"""

import json
import warnings
from collections import namedtuple
from datetime import datetime
from enum import IntEnum

from qiskit.circuit import QuantumCircuit, Parameter, Measure, Barrier
from qiskit.circuit.library import standard_gates
from qiskit.circuit.library.standard_gates import CZGate, RZGate, HGate, \
    GlobalPhaseGate, CXGate
from qiskit.providers import BackendV2 as Backend, Options, JobV1, QubitProperties
from qiskit.transpiler import Target, InstructionProperties, generate_preset_pass_manager

from .adapter import to_cqlib
from .api_client import ApiClient
from .gates import X2PGate, X2MGate, Y2MGate, Y2PGate, XY2MGate, XY2PGate, RxyGate
from .job import TianYanJob


# pylint: disable=invalid-name
class BackendType(IntEnum):
    """Enum representing the type of backend (quantum computer or simulator)."""
    quantum_computer = 0
    simulator = 1
    offline_simulator = 2


class BackendStatus(IntEnum):
    """Enum representing the status of the backend."""
    running = 0
    calibrating = 1
    under_maintenance = 2
    offline = 3


class CqlibAdapterError(Exception):
    """Base class for exceptions in this module."""


GateConfig = namedtuple('GateConfig', ['name', 'params', 'coupling_map'])

gate_parameters = {
    'rx': 1,
    'ry': 1,
    'rz': 1,
    'rxy': 2,
    'xy2p': 1,
    'xy2m': 1,
}


# pylint: disable=too-many-instance-attributes
class BackendConfiguration:
    """Class representing the configuration of a backend."""

    # pylint: disable=too-many-arguments,too-many-positional-arguments, too-many-locals
    def __init__(
            self,
            backend_id: str,
            backend_name: str,
            n_qubits: int,
            basis_gates: list,
            gates: list,
            local: bool,
            simulator: bool,
            conditional: bool,
            coupling_map: list,
            derivative_gates: list[str] = None,
            status: BackendStatus = None,
            supported_instructions: list[str] = None,
            credits_required: bool = None,
            online_date: datetime = None,
            display_name: str = None,
            description: str = None,
            tags: list = None,
            backend_type=None,
            machine_config=None,
            **kwargs,
    ):
        """Initializes the BackendConfiguration instance."""
        self.backend_id = backend_id
        self.backend_name = backend_name
        self.n_qubits = n_qubits
        self.basis_gates = basis_gates
        self.derivative_gates = derivative_gates
        self.gates = gates
        self.simulator = simulator
        self.conditional = conditional
        self.coupling_map = coupling_map
        self.local = local
        self.status = status
        self.supported_instructions = supported_instructions
        self.credits_required = credits_required
        self.online_date = online_date
        self.display_name = display_name
        self.description = description
        self.tags = tags
        self.properties = kwargs
        self.machine_config = machine_config
        self.backend_type = backend_type

    @staticmethod
    def from_dict(data: dict[str: str | int | list]) -> "BackendConfiguration":
        """Creates a BackendConfiguration instance from a dictionary.

        Args:
            data (dict): The dictionary containing backend configuration data.

        Returns:
            BackendConfiguration: The created BackendConfiguration instance.
        """
        return BackendConfiguration(**data)

    # pylint: disable=too-many-branches, too-many-locals
    @staticmethod
    def from_api(
            data: dict[str: str | int | list],
            api_client: ApiClient
    ) -> "BackendConfiguration":
        """Creates a BackendConfiguration instance from API data.

        Args:
            data (dict): The API data containing backend configuration.
            api_client (ApiClient):

        Returns:
            BackendConfiguration: The created BackendConfiguration instance.
        """
        disabled_qubits = [q for q in data['disabledQubits'].split(',') if q]
        disabled_couplers = [g for g in data['disabledCouplers'].split(',') if g]
        backend_id = data['id']
        n_qubits = data['bitWidth']

        if data['labels'] == '1':
            backend_type = BackendType.quantum_computer
        else:
            backend_type = BackendType.simulator

        if backend_type == BackendType.quantum_computer:
            qpu = api_client.get_quantum_computer_config(backend_id)
            qubits = [int(q[1:]) for q in qpu['qubits'] if q not in disabled_qubits]
            coupling_map = []

            for k, q in qpu['coupler_map'].items():
                if k in disabled_couplers:
                    continue
                q0, q1 = q
                if q0 in disabled_qubits or q1 in disabled_qubits:
                    continue
                coupling_map.append([int(q0[1:]), int(q1[1:])])
        else:
            qubits = list(range(n_qubits))
            # todo: 仿真机，比特太多了。先限制一下
            coupling_map = [[i, j] for i in range(min(n_qubits, 100)) for j in range(i)]
        basis_gates = []
        derivative_gates = []
        gates = []

        for gate in data['baseGate']:
            name = gate['qcis'].lower()
            rule = gate['rule']
            # to qiskit gate name
            if name == 'i':
                name = 'id'
            elif name == 'b':
                name = 'barrier'
            elif name == 'm':
                name = 'measure'
            basis_gates.append(name)

            try:
                rule = json.loads(rule)
            except json.JSONDecodeError:
                pass

            # coupler gate
            if isinstance(rule, dict) and 'topology' in rule:
                gate_coupling_map = coupling_map
            # single gate
            else:
                gate_coupling_map = [[q] for q in qubits]

            gates.append(GateConfig(
                name=name,
                params=[f'p_{i}' for i in range(gate_parameters.get(name, 0))],
                coupling_map=gate_coupling_map
            ))

        for gate in data['derivativeGate']:
            name = gate['qcis'].lower()
            if name not in basis_gates:
                derivative_gates.append(name)

        data = {
            'backend_id': backend_id,
            'backend_name': data['code'],
            'n_qubits': data['bitWidth'],
            'basis_gates': basis_gates,
            'derivative_gates': derivative_gates,
            'gates': gates,
            'local': False,
            'simulator': backend_type in [BackendType.simulator, BackendType.offline_simulator],
            'supported_instructions': basis_gates,
            'credits_required': data['isToll'] == 2,
            'status': BackendStatus(data['status']),
            'online_date': datetime.strptime(data['createTime'], '%Y-%m-%d %H:%M:%S'),
            'display_name': data['name'],
            'description': '',
            'conditional': False,
            'coupling_map': coupling_map,
            'backend_type': backend_type,
        }
        return BackendConfiguration.from_dict(data)


class TianYanBackend(Backend):
    """Base class for TianYan backends."""

    def __init__(
            self,
            configuration: BackendConfiguration,
            api_client: 'ApiClient',
    ) -> None:
        """Initializes the TianYanBackend instance.

        Args:
            configuration (BackendConfiguration): The configuration of the backend.
            api_client (ApiClient): The client for interacting with the API.
        """
        super().__init__(name=configuration.backend_name, )
        self.configuration = configuration
        self.resource_id = configuration.backend_id
        self.resource_type = configuration.backend_id
        self.simulator = configuration.simulator
        self._api_client = api_client
        self._target = None
        self._machine_config = {}

    @classmethod
    def _default_options(cls):
        """Returns the default options for the backend.

        Returns:
            Options: The default options.
        """
        return Options()

    @property
    def max_circuits(self):
        """Returns the maximum number of circuits that can be executed in a single job.

        Returns:
            int: The maximum number of circuits.
        """
        return 50

    @property
    def machine_config(self):
        """Returns the machine configuration.

        Returns:
            dict: The machine configuration.
        """
        return self._machine_config

    @property
    def backend_type(self):
        """Returns the type of the backend.

        Returns:
            BackendType: The type of the backend.
        """
        return self.configuration.backend_type

    def run(
            self,
            run_input,
            shots: int = 1024,
            readout_calibration: bool = True,
            auto_transpile: bool = True,
            **options
    ) -> JobV1:
        """Submits a job to the backend.

        Args:
            run_input (QuantumCircuit | list[QuantumCircuit]): The circuit(s) to execute.
            shots (int, optional): The number of shots to execute. Defaults to 1024.
            readout_calibration (bool, optional): Whether to perform readout calibration.
                Defaults to True.
            auto_transpile (bool, optional): Automatically perform circuit compile on the backend.
            **options: Additional options for the job.

        Returns:
            JobV1: The submitted job.

        Raises:
            TypeError: If the input type is not supported.
        """
        if isinstance(run_input, QuantumCircuit):
            circuits = [run_input]
        elif isinstance(run_input, list):
            circuits = run_input
        else:
            raise TypeError(f"Unsupported input type: {type(run_input)}")

        if auto_transpile:
            pm = generate_preset_pass_manager(backend=self)
            circuits = [pm.run(qc) for qc in circuits]

        task_ids = self._api_client.submit_job(
            [to_cqlib(circ) for circ in circuits],
            machine=self.configuration.backend_name,
            shots=shots,
        )
        return TianYanJob(
            backend=self,
            job_id=','.join(task_ids),
            api_client=self._api_client,
            shots=shots,
            readout_calibration=readout_calibration,
            **options
        )

    @property
    def target(self):
        """Returns the target for the backend.

        Returns:
            Target: The target for the backend.
        """
        return self._target

    def __repr__(self) -> str:
        """Returns a string representation of the backend.

        Returns:
            str: The string representation.
        """
        return f"<{self.__class__.__name__}('{self.name}')>"


time_units = {
    's': 1,
    'ms': 1e-3,
    'us': 1e-6,
    'ns': 1e-9
}
frequency_units = {
    'hz': 1,
    'khz': 1e3,
    'mhz': 1e6,
    'ghz': 1e9
}
number_units = {
    '%': 1e-2,
    '': 1
}


class TianYanQuantumBackend(TianYanBackend):
    """Class representing a quantum computer backend on the TianYan platform."""

    def __init__(
            self,
            configuration: BackendConfiguration,
            api_client: 'ApiClient',
    ) -> None:
        """Initializes the TianYanQuantumBackend instance.

        Args:
            configuration (BackendConfiguration): The configuration of the backend.
            api_client (ApiClient): The client for interacting with the API.
        """
        super().__init__(configuration=configuration, api_client=api_client)
        self._machine_config = self._api_client.get_quantum_machine_config(
            self.configuration.backend_name
        )
        target = Target(
            # num_qubits=configuration.n_qubits,
            description=configuration.backend_name,
            qubit_properties=self._make_qubit_properties()
        )
        self._update_cz_gate(target)
        self._update_single_gates(target)
        self._update_measure_gate(target)
        self._update_barrier_gate(target)
        self._target = target

    # pylint: disable=too-many-locals
    def _make_qubit_properties(self):
        """Creates qubit properties from the machine configuration.

        Returns:
            list[QubitProperties | None]: The list of qubit properties.
        """
        t1 = self._machine_config['qubit']['relatime']['T1']
        t1_qubits = t1['qubit_used']
        t1_values = t1['param_list']
        t1_unit = time_units.get(t1['unit'].lower())
        t2 = self._machine_config['qubit']['relatime']['T2']
        t2_qubits = t2['qubit_used']
        t2_values = t2['param_list']
        t2_unit = time_units.get(t2['unit'].lower())
        frequency = self._machine_config['qubit']['frequency']['f01']
        frequency_qubits = frequency['qubit_used']
        frequency_values = frequency['param_list']
        frequency_unit = frequency_units.get(frequency['unit'].lower())

        if t1_qubits != t2_qubits != frequency_qubits:
            raise ValueError("t1/t2/frequency qubits are not the same")
        qubit_properties: list[QubitProperties | None] = [
            None for _ in range(self.configuration.n_qubits)
        ]
        for i, q in enumerate(t1_qubits):
            qubit_properties[int(q[1:])] = QubitProperties(
                t1=t1_values[i] * t1_unit,
                t2=t2_values[i] * t2_unit,
                frequency=frequency_values[i] * frequency_unit
            )
        return qubit_properties

    def _update_cz_gate(self, target: Target):
        """Updates the CZ gate in the target.

        Args:
            target (Target): The target to update.
        """
        cz_props = {}
        coupler_map = self._machine_config['overview']['coupler_map']
        gate_errors = self._machine_config['twoQubitGate']['czGate']['gate error']
        error_qubits = gate_errors['qubit_used']
        error_values = gate_errors['param_list']
        error_unit = number_units[gate_errors['unit']]

        for i, q in enumerate(error_qubits):
            q0, q1 = coupler_map[q]
            q0, q1 = int(q0[1:]), int(q1[1:])
            p = InstructionProperties(error=error_values[i] * error_unit, duration=1e-8)
            cz_props[q0, q1] = p
            cz_props[q1, q0] = p
        if 'cz' in self.configuration.basis_gates:
            target.add_instruction(CZGate(), cz_props)

    def _update_single_gates(self, target: Target):
        """Updates the single-qubit gates in the target.

        This method adds single-qubit gates (e.g., RZ, X2P, X2M, Y2P, Y2M, XY2P, XY2M)
        to the target based on the backend's configuration. It also includes the HGate
        and GlobalPhaseGate.

        Args:
            target (Target): The target to update with single-qubit gates.
        """
        rz_props = {}
        single_props = {}

        gate_params = self._machine_config['qubit']['singleQubit']['gate error']
        gate_values = gate_params['param_list']
        gate_qubits = gate_params['qubit_used']
        gate_unit = number_units[gate_params['unit']]

        for i, q in enumerate(gate_qubits):
            q_index = (int(q[1:]),)
            rz_props[q_index] = InstructionProperties(error=0, duration=0)
            single_props[q_index] = InstructionProperties(
                error=gate_values[i] * gate_unit,
                duration=0
            )
        if 'rz' in self.configuration.basis_gates:
            target.add_instruction(RZGate(Parameter('theta')), rz_props)
        if 'x2p' in self.configuration.basis_gates:
            target.add_instruction(X2PGate(), single_props.copy())
            # HGate is very import.
            target.add_instruction(HGate(), single_props.copy())
        if 'x2m' in self.configuration.basis_gates:
            target.add_instruction(X2MGate(), single_props.copy())
        if 'y2p' in self.configuration.basis_gates:
            target.add_instruction(Y2PGate(), single_props.copy())
        if 'y2m' in self.configuration.basis_gates:
            target.add_instruction(Y2MGate(), single_props.copy())
        if 'xy2p' in self.configuration.basis_gates:
            target.add_instruction(XY2PGate(Parameter('theta')), single_props.copy())
        if 'xy2m' in self.configuration.basis_gates:
            target.add_instruction(XY2MGate(Parameter('theta')), single_props.copy())

        target.add_instruction(GlobalPhaseGate(Parameter('phase')), {(): None})

    def _update_measure_gate(self, target: Target):
        """Updates the measurement gate in the target.

        This method adds the measurement gate to the target based on the backend's
        configuration and readout error data.

        Args:
            target (Target): The target to update with the measurement gate.
        """
        gate_params = self._machine_config['readout']['readoutArray']['Readout Error']
        gate_values = gate_params['param_list']
        gate_qubits = gate_params['qubit_used']
        gate_unit = number_units[gate_params['unit']]
        props = {
            (int(q[1:]),): InstructionProperties(error=gate_values[i] * gate_unit, duration=0)
            for i, q in enumerate(gate_qubits)
        }
        target.add_instruction(Measure(), props)

    def _update_barrier_gate(self, target: Target):
        """Updates the barrier gate in the target.

        This method adds the barrier gate to the target if it is supported by the
        backend's configuration.

        Args:
            target (Target): The target to update with the barrier gate.
        """
        if 'barrier' in self.configuration.basis_gates:
            target.add_instruction(Barrier, name="barrier")


class TianYanSimulatorBackend(TianYanBackend):
    """Class representing a simulator backend on the TianYan platform.

    This class extends the TianYanBackend to handle simulator-specific configurations
    and operations.
    """

    def __init__(
            self,
            configuration: BackendConfiguration,
            api_client: 'ApiClient',
    ) -> None:
        """Initializes the TianYanSimulatorBackend instance.

        Args:
            configuration (BackendConfiguration): The configuration of the simulator backend.
            api_client (ApiClient): The client for interacting with the API.
        """
        super().__init__(configuration=configuration, api_client=api_client)
        target = Target(
            num_qubits=configuration.n_qubits,
            description=configuration.backend_name,
        )
        self._update_gates(target)
        self._target = target

    def _update_gates(self, target):
        """Updates the gates in the target for the simulator backend.

        This method adds all supported gates (single-qubit, two-qubit, and measurement gates)
        to the target based on the backend's configuration.

        Args:
            target (Target): The target to update with the gates.
        """
        q_props = {(q,): None for q in range(self.configuration.n_qubits)}
        gates = set(self.configuration.basis_gates + self.configuration.derivative_gates)
        ins_mapping_list = {
            'rx': [standard_gates.RXGate(Parameter('theta')), q_props],
            'ry': [standard_gates.RYGate(Parameter('theta')), q_props],
            'rz': [standard_gates.RZGate(Parameter('theta')), q_props],
            'x2p': [X2PGate(), q_props],
            'x2m': [X2MGate(), q_props],
            'y2p': [Y2PGate(), q_props],
            'y2m': [Y2MGate(), q_props],
            'xy2p': [XY2PGate(Parameter('theta')), q_props],
            'xy2m': [XY2MGate(Parameter('theta')), q_props],
            'h': [standard_gates.HGate(), q_props],
            'x': [standard_gates.XGate(), q_props],
            'y': [standard_gates.YGate(), q_props],
            'z': [standard_gates.ZGate(), q_props],
            's': [standard_gates.SGate(), q_props],
            'sd': [standard_gates.SdgGate(), q_props],
            't': [standard_gates.TGate(), q_props],
            'td': [standard_gates.TdgGate(), q_props],
            'rxy': [RxyGate(Parameter('phi'), Parameter('theta')), q_props],

            'measure': [Measure(), q_props],
        }
        ins_mapping_dict = {
            'cz': {'instruction': CZGate(), 'properties': {None: None}},
            'cx': {'instruction': CXGate(), 'properties': {None: None}},
            'barrier': {'instruction': Barrier, 'name': 'barrier'}
        }
        for gate in gates:
            if gate in ins_mapping_list:
                target.add_instruction(*ins_mapping_list[gate])
            elif gate in ins_mapping_dict:
                target.add_instruction(**ins_mapping_dict[gate])
            elif gate == 'id':
                pass
            else:
                warnings.warn(f'{gate} is not supported in simulator backend.')
