# Quantum Key Distribution (QKD) Simulation: BB84 Protocol

This project is a **simulation of the BB84 Quantum Key Distribution protocol** developed for the Quantum Information Processing course I followed at Politecnico di Milano.\
The BB84 protocol, introduced by Charles Bennett and Gilles Brassard, is a foundational quantum cryptography method, utilizing the unique properties of quantum mechanics to securely establish encryption keys between two parties.

## Overview

In this simulation:
- **Alice** and **Bob** are the two parties aiming to establish a secure key.
- **Eve** acts as a potential eavesdropper, trying to intercept the key exchange.
- The protocol demonstrates how quantum mechanics, specifically the **No Cloning Theorem** and **qubit superposition**, enables detection of eavesdropping attempts.

For a comprehensive understanding of the project, refer to the [full project report](./Report-Maiuolo_Manuel-QKD_Simulation_BB84_Protocol.pdf), which includes:
- Detailed **protocol mechanics**
- **Classical cryptography** background
- **Simulation examples** for ideal conditions and eavesdropped scenarios

## Installation

To run this simulation, ensure you have:
- **Python 3.10+** installed on your device. You can download Python [here](https://www.python.org/downloads/).

Then [download the repository as a ZIP file](https://github.com/BestPlayerMMIII/BB84/archive/refs/heads/main.zip).

### Running the Simulation

1. **Server Setup**: Start the `BB84_server.py`, which coordinates the QKD process.
2. **Participants**:
   - Run `BB84_Alice.py` and `BB84_Bob.py` for standard key exchange.
   - Optionally, run `BB84_Eve.py` to simulate an eavesdropper.
3. **Commands**: Interact with each component through the Command Line Interface (CLI) to simulate QKD steps.

## Example Scenarios

### 1. **Ideal Conditions**: 
   - Alice and Bob exchange qubits over a **quantum channel** and detect any basis mismatches through a **classical channel**.
   - The shared key is established without interference, ensuring secure encryption.

### 2. **Eavesdropper Present**: 
   - With Eve eavesdropping, any attempt to intercept qubits can disrupts their quantum state, making her presence detectable.
   - Alice and Bob identify inconsistencies in the shared key, revealing Eve’s interference.

## Documentation and Usage

This project is organized as follows:
- **BB84lib.py**: Core library for handling qubit states and basis.
- **CUlib.py**: Utility functions for CLI interaction and communication.
- **Server and Client Classes**: Control the key distribution process across participants.

For further details, please see the **documentation section** in the [full project report](./Report-Maiuolo_Manuel-QKD_Simulation_BB84_Protocol.pdf).

## License

This project is open-source and available under the [MIT License](./LICENSE).

---

For questions, please refer to the **report documentation** or open an issue.
