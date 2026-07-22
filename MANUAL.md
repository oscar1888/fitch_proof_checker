# User Manual: Fitch Proof Checker

## 1. Introduction
The **Fitch Proof Checker** is an interactive environment for building and formally verifying proofs in natural deduction, based on the Fitch-style calculus. The system allows users to manage premises, open subproofs with temporary assumptions, and apply inference rules, ensuring the formal correctness of every single step.

## 2. User Interface
The main interface is designed to facilitate the drafting and checking of proofs. It consists of:

* **Workspace (Editor):** The central section where the lines of the proof are structured.
* **Menu Bar:** Provides access to the main application commands, organized by category:
  * **File:** Manage proofs as files (save/load), open new instances of the program, and exit.
  * **Edit:** Perform standard text editing operations.
  * **View:** Adjust the zoom level of the interface.
  * **Proof:** Modify the overall structure of the proof and run verifications.
  * **Logic:** Manipulate the grammar used in the proof (specifically connectives and quantifiers) and manage the set of inference rules available for justifications.
  * **Help:** View keyboard shortcuts for inserting special logical symbols.
* **Verification Area:** A dedicated section containing buttons for step-by-step or full proof verification.
* **Logic Descriptor:** An indicator displaying the logical system currently in use.
* **Goal Field:** A specific input field to define the final target formula to be proven.
* **Information Box:** A panel dedicated to displaying system messages, validation feedback, and errors.

## 3. Building a Proof
A proof is built iteratively, specifying the formula and its logical justification for each line. To manage this process, the editor provides the following structural elements:

* **Formula:** Each line requires entering a well-formed formula according to the currently loaded grammar (e.g. in FOL, `∀x (P(x) → Q(x))`).
* **Subproofs:** It is possible to open a new logical context by introducing an assumption. When setting up these assumptions, it is also possible to introduce or eliminate arbitrary constants. The editor visually indicates the nesting depth level.
* **Justification:** Every line that is not an assumption features a specific justification field. Here, you must specify the applied inference rule by typing its name, followed by a (possibly empty) sequence of line numbers to indicate a single step (e.g. `4`) and/or line ranges to indicate subproofs (e.g., `8-12`) separated by commas, which act as the cited references for the justification (e.g. `∨Elim 4, 5-6, 7-8`).
> **Tip for a Fluid Workflow:** For a smoother and faster editing experience, it is highly recommended to use the keyboard shortcuts indicated in the Menu Bar (those in **Menu Bar > Proof** and **Menu Bar > Help > Special symbols shortcuts**). These shortcuts allow for quick manipulation of the proof's structure and the rapid insertion of special logical symbols.

## 4. Verifying a Proof
The validation engine allows you to ensure the correctness of your derivation either incrementally or all at once.

* **Step-by-Step Verification:** You can verify the proof one step at a time by placing your cursor (focus) on any specific line (any text field selected on the line is valid) and pressing the **Check Step** button.
* **Full Verification:** You can verify the entire derivation by pressing the **Check Proof** button. This will check every step sequentially from the first to the last. If all steps are correct, the system will finally verify whether the optional target formula (specified in the Goal field) has been successfully reached in the last line.

**Status Indicators:** Next to every non-assumption line, there is a status dot. Upon running a verification (either step-by-step or full), this dot turns green if the step is logically correct, or red if an error is detected.

## 5. Grammar Management
The editor allows you to abstract from a single fixed calculus and adapt to different logics or conventions by dynamically extending the logical alphabet.

By navigating to **Logic > Manage grammar** in the Menu Bar, you will open the Grammar Manager. This interface allows you to:
* Add or remove connectives and quantifiers. *(Note: You can only remove custom elements; native core components cannot be deleted).*
* Reset the grammar to a predefined preset.
* Save the complete grammar configuration to a JSON profile on your disk, or load an existing one, ensuring the portability of your setup across different workspaces.

### Adding Custom Elements via Plugins

**Custom Connectives:**
Provide a `.py` file containing a `CustomConnective` class that inherits from `Connective`. You must define the `name`, `symbol`, and `arity`. 
Here is an example for the XOR connective:

```python
from fitch_proof_checker.model.formula.connective import Connective

class CustomConnective(Connective):
    name = "Xor"
    symbol = "XOR"
    arity = 2
```

**Custom Quantifiers:**
Similarly, you can define a new quantifier by providing a `.py` file with a `CustomQuantifier` class that defines `name` and `symbol`, and inherits from `Quantifier`:

```python
from fitch_proof_checker.model.formula.quantifier import Quantifier

class CustomQuantifier(Quantifier):
    name = "Exists Unique"
    symbol = "∃!"
```

### Using Custom Elements in the Editor
Once loaded, the new connective or quantifier becomes immediately available for syntactic validation. However, to distinguish them from standard propositional variables or predicates, **all custom elements must be escaped with a backslash (`\ `)** when typed into a proof line.

*   **Quantifier example:** `\∃!x P(x)`
*   **Connective example:** `\XOR(A, B)`

> **Important Syntax Rule:** Custom connectives *always* follow a strict functional syntax. Regardless of their arity, the connective symbol must be followed by its arguments enclosed in parentheses and separated by commas, as shown in the XOR example above.

### Dynamic Grammar Schema and Lexical Rules

Behind the scenes, the editor dynamically generates a parser grammar string every time the logical alphabet is updated. The structure of this grammar is defined by the following schema template, where custom and standard elements are injected into the respective blocks:

```python
dynamic_grammar = f"""
    ?start: formula

    ?formula: {formula_alternatives}

    {dynamic_binary_block}

    ?formula_un: UNARY_OP formula_un -> un_op
               | QUANTIFIER VAR_NAME formula_un -> quantified
               | formula_atom

    ?formula_atom: term "=" term -> eq
                 | NARY_OP "(" formula ("," formula)* ")" -> nary_op
                 | PRED_NAME "(" term ("," term)* ")" -> pred
                 | PRED_NAME -> prop_var
                 | NULLARY_OP -> nullary_op
                 | "(" formula ")"
                 | "[" formula "]"
                 | "{{" formula "}}"

    ?term: FUNC_NAME "(" term ("," term)* ")" -> func
         | FUNC_NAME -> const
         | VAR_NAME -> var

    {dynamic_terminals_block}

    UNARY_OP: {rule_unary}
    NULLARY_OP: {rule_nullary}
    NARY_OP: {rule_nary}
    QUANTIFIER: {rule_quant}

    VAR_NAME: /[n-z]+/
    FUNC_NAME: /[a-m]+/
    PRED_NAME: /[A-Z][a-zA-Z]*/

    %import common.WS
    %ignore WS
"""
```

**Note:** Although it is not explicitly apparent from the dynamic grammar defined above, it has been established by convention within the system that all infix binary operators are treated as left-associative by the parser.

**Strict Naming Conventions**
When writing formulas in the editor, it is critical to adhere to the lexical rules defined at the bottom of this schema. The parser strictly enforces the following regex-based conventions to distinguish between different logical components:

*   **Variables (`VAR_NAME`):** Must consist exclusively of one or more lowercase letters in the range **n through z** (e.g., `x`, `y`, `z`, `xx`). Numbers are not allowed.
*   **Functions and Constants (`FUNC_NAME`):** Must consist exclusively of one or more lowercase letters in the range **a through m** (e.g., `a`, `b`, `c`, `f`, `g`).
*   **Predicates and Propositional Variables (`PRED_NAME`):** Must begin with an **uppercase letter**, optionally followed by any combination of uppercase and lowercase letters (e.g., `P`, `Q`, `Pred`, `IsEven`).

## 6. Logic Management
By navigating to **Logic > Manage logic** in the Menu Bar, you will open the Logic Manager. Similar to the Grammar Manager, this interface allows you to:
* Add or remove inference rules. *(Unlike grammar components, you can remove even the standard First-Order Logic (FOL) rules to build a strictly customized system).*
* Reset the logic to a predefined default preset.
* Save the complete set of active rules to a JSON profile file, or load an existing one.
### Adding Custom Rules via Plugins
You can inject new inference rules by providing a Python file (`.py`) containing a class named `CustomRule` that inherits from `Rule`. This class must define a `name` attribute (which will be the string typed in the justification field by the user) and a static `check` method that validates the rule application.

The signature for the check method is:
```python
check(ipp, actual_premises, actual_conclusion) -> bool
```

*   **`ipp` (Input Proof Presenter):** An interface to query the global state of the proof. It exposes the useful method `constant_occurs_outside_subproof(const, lines_range)`. You pass a `Const` object (e.g., `Const('a')`) and a tuple of integers representing the subproof's line range, and it returns whether that constant escapes the subproof's scope.
*   **`actual_premises`:** A list containing `Formula` or `Subproof` objects cited in the justification.
*   **`actual_conclusion`:** The `Formula` object representing the current line to be verified.

Here is a practical example for a Custom Rule implementing the XOR Introduction:

```python
from fitch_proof_checker.model.formula.connective import Not
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule

class CustomRule(Rule):
    name = "\\XorIntro"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        # We need exactly two premises
        if len(actual_premises) != 2:
            return False

        # None of the premises can be a subproof
        if isinstance(actual_premises[0], Subproof) or isinstance(actual_premises[1], Subproof):
            return False

        # The conclusion must be a CustomConnective named "Xor"
        if (type(actual_conclusion).__name__ != "CustomConnective"
                or actual_conclusion.name != "Xor"):
            return False

        p1, p2 = actual_premises
        left_node = actual_conclusion.args[0]
        right_node = actual_conclusion.args[1]

        # XOR Introduction logic: (A and ~B) or (~A and B) implies (A XOR B)
        if (p1 == left_node and p2 == Not(right_node)) or \
           (p2 == left_node and p1 == Not(right_node)):
            return True

        if (p1 == Not(left_node) and p2 == right_node) or \
           (p2 == Not(left_node) and p1 == right_node):
            return True

        return False
```

### Type Checking Custom Elements
When writing your `check` method, you must be careful when verifying if an object is a custom connective or quantifier. Because plugins are loaded dynamically at runtime, the imported module and the dynamically loaded module are treated as distinct by Python. 

Therefore, **you cannot use `isinstance()` or the `is` operator** for custom objects. Doing `type(actual_conclusion) is Xor` or `isinstance(actual_conclusion, Xor)` will fail.

Instead, you must check the string representation of the class name and the object's `name` attribute:
```python
# CORRECT WAY:
type(actual_conclusion).__name__ == "CustomConnective" and actual_conclusion.name == "Xor"
```

### Overview of AST Classes
To effectively write custom rules, you will need to manipulate Abstract Syntax Tree (AST) nodes. Here is a brief overview of the class hierarchy and available methods/attributes passed to the `check` method:

**`ASTNode` (Base Class):**
*   `free_vars() -> set`: Returns the set of free variables occurring in the node.
*   `match_instantiation(other, allowed_vars, mapping=None) -> bool`: Checks if `other` is a valid instantiation of `self` by substituting `allowed_vars`, using a `mapping` dictionary.
*   `is_eq_subst(target, t1, t2) -> bool`: Evaluates if `self` is equal to `target` under the assumption that `t1 = t2`.
*   `contains(other) -> bool`: Checks if the current node contains the `other` node.
*   `is_alpha_equiv(other, mapping=None) -> bool`: Checks if `self` is alpha-equivalent to `other` (i.e., identical up to renaming of bound variables).
*   `subst(to_subst, substituend)`: Replaces occurrences of `to_subst` with `substituend` inside `self`.

**`Formula` and `Term` (Inherit from `ASTNode`):**
These base classes are extended by specific logical elements. Below are their subclasses and the specific attributes they expose:

**Subclasses of `Term`**:
*   **`Const`**: 
    *   Attributes: `name` (str).
*   **`Func`**: 
    *   Attributes: `name` (str), `args` (tuple of Term).
*   **`Var`**: 
    *   Attributes: `name` (str).

**Subclasses of `Formula`**:
*   **`Connective`**: 
    *   Attributes: `args` (tuple of Formula), `name` (str), `symbol` (str), `arity` (int).
*   **`Predicate`**: 
    *   Attributes: `name` (str), `args` (tuple of Term).
*   **`PropVar`**: 
    *   Attributes: `name` (str).
*   **`Quantifier`**: 
    *   Attributes: `variable` (Var), `subformula` (Formula), `name` (str), `symbol` (str).

**`Subproof` attributes:**
*   `constants` (list of str): Arbitrary constants introduced in this subproof's assumption.
*   `lines_range` (tuple of int): The starting and ending line numbers `(start, end)`.
*   `assumption` (Formula): The premise formula of the subproof.
*   `lines` (list of Formula): The derived lines within the subproof.

## Examples

If you are looking for inspiration or want to study more complex implementations, you can consult the standard components and test files included in the project. Reviewing the source code provides good templates not only for handling various logical scenarios and AST manipulations for inference rules, but also for defining custom grammar elements and structuring proofs.

You can find these reference implementations in the following project subpackages:

* **`fitch_proof_checker.model.rule`**: Contains the core, natively supported FOL rules (e.g., Modus Ponens, Universal Instantiation).
* **`tests.rules`**: Contains additional rule examples used for testing the system's extensibility (e.g. DeMorgan, Modus Tollens).
* **`tests.grammar`**: Provides reference implementations of custom connectives and quantifiers to help you build your own alphabet extensions.
* **`tests.proof`**: Contains various examples of successfully verified proofs that you can load and study within the editor.