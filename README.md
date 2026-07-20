# Fitch proof checker

Master’s thesis project implementing an environment for developing and verifying proofs in natural deduction calculi.

The system handles Fitch-style proofs, representing derivations through structured lines and subproofs that make assumptions and inference rule applications explicit.

It includes support for managing and extending the set of rules, allowing the definition of sound and complete calculi for different logical systems.

## Requirements
- Python 3.10 or higher

## Installation and Execution

Open your terminal, navigate to the root directory of the project, and follow these steps:

1. **Install dependencies:**
   Before running the application, you need to install the required packages via the `requirements.txt` file:
   
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the editor:**
   Since the project contains a `__main__.py` file in the main directory, you can launch the application simply by executing:
   
   ```bash
   python .
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
