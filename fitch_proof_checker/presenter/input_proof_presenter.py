from PyQt6.QtWidgets import QApplication
from lark.exceptions import LarkError
from fitch_proof_checker.model.formula import JustifiedLine, Subproof
from fitch_proof_checker.model.justification import parse_justification
from fitch_proof_checker.model.parse_error import ParseError
from fitch_proof_checker.view.proof_layout import get_all_lines, find_final_subproof_idx, get_premises
from fitch_proof_checker.view.utils.misc import set_status


class InputProofPresenter:
    def __init__(self, fpe_main_window, model):
        self.fpe_main_window = fpe_main_window
        self.model = model
        fpe_main_window.add_input_proof_presenter(self)

    def constant_occurs_outside_subproof(self, const, lines_range):
        all_lines = get_all_lines(self.fpe_main_window)
        st_idx, end_idx = lines_range[0] - 1, lines_range[1] - 1
        lines_to_inspect = all_lines[:st_idx]
        formula_parser = self.model.grammar_manager.formula_parser
        for line in lines_to_inspect:
            try:
                ast = formula_parser(line.formula_field.text().strip())
                if ast and ast.contains(const) and find_final_subproof_idx(self.fpe_main_window, line) >= st_idx: return True
            except (LarkError, ValueError):
                pass
        return False

    def _set_line_feedback(self, proof_line, is_valid: bool, msg: str):
        set_status(proof_line.status_dot, is_valid)
        self.fpe_main_window.log_console.setText(msg)

    def _parse_formula(self, current_line):
        formula_text = current_line.formula_field.text().strip()
        try:
            return self.model.grammar_manager.formula_parser(formula_text)
        except LarkError as e:
            raise ParseError(f"Syntax error:\n{e.get_context(formula_text)}")
        except ValueError as e:
            raise ParseError(f"Syntax error: {str(e)}")

    @staticmethod
    def _parse_justification(current_line):
        try:
            return parse_justification(current_line.justification_field.text().strip())
        except (LarkError, ParseError) as e:
            raise ParseError(f"Justification syntax error: {str(e)}")

    @staticmethod
    def _parse_single_cited_line(ref, all_lines,
                                 current_index, current_line, premises_num, formula_parser, cited_items):
        line_idx = ref - 1

        if line_idx < 0 or line_idx >= len(all_lines):
            raise ValueError(f"Line {ref} is out of bounds.")
        if line_idx >= current_index:
            raise ValueError(f"Cannot cite future or current lines ({ref}).")

        cited_line = all_lines[line_idx]

        if cited_line.depth > current_line.depth:
            raise ValueError(f"Line {ref} is trapped inside a closed subproof.")

        for i in range(line_idx + 1, current_index):
            if all_lines[i].depth < cited_line.depth:
                raise ValueError(f"The subproof containing line {ref} has been closed.")
            if all_lines[i].depth == cited_line.depth and all_lines[i].is_assump and i >= premises_num:
                raise ValueError(f"Line {ref} belongs to a parallel subproof that is already closed.")

        try:
            cited_line_ast = formula_parser(cited_line.formula_field.text().strip())
        except LarkError:
            raise ValueError(f"Syntax error in the formula at cited line {ref}.")

        cited_items.append(cited_line_ast)

    def _parse_cited_subproof(self, ref, all_lines, current_index, current_line, formula_parser, cited_items):
        start_idx, end_idx = ref[0] - 1, ref[1] - 1

        if start_idx < 0 or end_idx >= len(all_lines):
            raise ValueError(f"Subproof {ref[0]}-{ref[1]} is out of bounds.")

        if end_idx >= current_index:
            raise ValueError(f"Cannot cite future or current lines ({ref[0]}-{ref[1]}).")
        if start_idx > end_idx:
            raise ValueError(f"Invalid interval ({ref[0]}-{ref[1]}).")

        start_line = all_lines[start_idx]
        end_line = all_lines[end_idx]

        if start_line.depth != end_line.depth:
            raise ValueError(f"Subproof {ref[0]}-{ref[1]} has misaligned depths.")
        if not start_line.is_assump:
            raise ValueError(f"Line {ref[0]} is not an assumption.")

        actual_end = find_final_subproof_idx(self.fpe_main_window, start_line)
        if actual_end != end_idx:
            raise ValueError(f"Partial citation ({ref[0]}-{ref[1]}).")

        if start_line.depth != current_line.depth + 1:
            raise ValueError(f"Subproof {ref[0]}-{ref[1]} is not accessible from this depth.")

        stack = []

        for i in range(start_idx, end_idx + 1):
            line = all_lines[i]

            while len(stack) > 1:
                top_depth = stack[-1]['start_line'].depth
                if top_depth > line.depth or (line.is_assump and top_depth == line.depth):
                    popped = stack.pop()
                    popped_range = (popped['start_idx'] + 1, i)
                    subproof_obj = Subproof(
                        popped['start_line'].arb_consts_introduced,
                        popped_range,
                        popped['assump_ast'],
                        popped['body_asts']
                    )
                    stack[-1]['body_asts'].append(subproof_obj)
                else:
                    break

            try:
                ast = formula_parser(line.formula_field.text().strip())
            except LarkError:
                raise ValueError(f"Syntax error inside the formula at line {i + 1}.")

            if line.is_assump:
                stack.append({
                    'start_idx': i,
                    'start_line': line,
                    'assump_ast': ast,
                    'body_asts': []
                })
            else:
                if not stack:
                    raise ValueError(f"Line {i + 1} is not within any subproof context.")
                stack[-1]['body_asts'].append(ast)

        while len(stack) > 1:
            popped = stack.pop()
            popped_range = (popped['start_idx'] + 1, end_idx + 1)
            subproof_obj = Subproof(
                popped['start_line'].arb_consts_introduced,
                popped_range,
                popped['assump_ast'],
                popped['body_asts']
            )
            stack[-1]['body_asts'].append(subproof_obj)

        if not stack:
            raise ValueError(f"Error parsing subproof {ref[0]}-{ref[1]}: empty stack.")

        root_data = stack.pop()
        lines_range = (root_data['start_idx'] + 1, end_idx + 1)
        root_subproof = Subproof(
            root_data['start_line'].arb_consts_introduced,
            lines_range,
            root_data['assump_ast'],
            root_data['body_asts']
        )

        cited_items.append(root_subproof)

    def _parse_cited_lines(self, current_line, parsed_just):
        if not parsed_just['references']: return []
        formula_parser = self.model.grammar_manager.formula_parser
        all_lines = get_all_lines(self.fpe_main_window)
        current_index = all_lines.index(current_line)
        premises_num = len(get_premises(self.fpe_main_window))
        cited_items = []
        try:
            for ref in parsed_just['references']:
                if isinstance(ref, tuple):
                    self._parse_cited_subproof(ref, all_lines, current_index, current_line, formula_parser, cited_items)
                else:
                    InputProofPresenter._parse_single_cited_line(
                        ref, all_lines, current_index, current_line, premises_num, formula_parser, cited_items
                    )
        except ValueError as e:
            raise ParseError(f"Citation error: {str(e)}")

        return cited_items

    def check_step(self):
        focus_widget = QApplication.instance().focusWidget()
        if not hasattr(focus_widget, 'proof_line'): return
        current_line = focus_widget.proof_line
        if current_line.is_assump: return

        try:
            parsed_formula = self._parse_formula(current_line)
            parsed_just = InputProofPresenter._parse_justification(current_line)
            cited_items = self._parse_cited_lines(current_line, parsed_just)
            is_valid = self.model.check_step(self, cited_items, JustifiedLine(parsed_formula, parsed_just))
        except (ParseError, ValueError) as e:
            self._set_line_feedback(current_line, False, str(e))
            return

        self._set_line_feedback(current_line, is_valid, "")

    def check_proof(self):
        all_lines = get_all_lines(self.fpe_main_window)
        proof_is_valid = True
        first_error_msg = None
        last_parsed_formula = None
        has_derived_steps = False

        for idx, current_line in enumerate(all_lines):
            try:
                parsed_formula = self._parse_formula(current_line)
                last_parsed_formula = parsed_formula
                if current_line.is_assump: continue
                has_derived_steps = True

                parsed_just = self._parse_justification(current_line)
                cited_items = self._parse_cited_lines(current_line, parsed_just)
                is_valid = self.model.check_step(self, cited_items, JustifiedLine(parsed_formula, parsed_just))

                if not is_valid:
                    raise ValueError(f"Invalid application of rule '{parsed_just.get('rule', 'Unknown')}'.")

                set_status(current_line.status_dot, True)

            except (ParseError, ValueError) as e:
                set_status(current_line.status_dot, False)
                proof_is_valid = False

                if first_error_msg is None:
                    first_error_msg = f"Error at line {idx + 1}: {str(e)}"

        if proof_is_valid:
            try:
                if not has_derived_steps:
                    raise ValueError("The proof must contain at least one derived step which cannot be an assumption.")

                goal_text = self.fpe_main_window.goal_field.text().strip()
                parsed_goal = self.model.grammar_manager.formula_parser(goal_text)
                if parsed_goal is None:
                    set_status(self.fpe_main_window.goal_status_dot, None)
                    return

                if last_parsed_formula != parsed_goal or all_lines[-1].depth > 0:
                    raise ValueError()

                set_status(self.fpe_main_window.goal_status_dot, True)
            except (LarkError, ParseError) as e:
                set_status(self.fpe_main_window.goal_status_dot, False)
                self.fpe_main_window.log_console.setText(f"Goal Syntax Error:\n\t{str(e)}")
            except ValueError as e:
                set_status(self.fpe_main_window.goal_status_dot, False)
                self.fpe_main_window.log_console.setText(str(e))
        else:
            set_status(self.fpe_main_window.goal_status_dot, False)
            self.fpe_main_window.log_console.setText(first_error_msg)

    def serialize_proof(self) -> dict:
        all_lines = get_all_lines(self.fpe_main_window)

        proof_data = {
            "goal": self.fpe_main_window.goal_field.text(),
            "lines": []
        }

        for line in all_lines:
            line_data = {
                "formula": line.formula_field.text(),
                "justification": line.justification_field.text() if not line.is_assump else None,
                "depth": line.depth,
                "is_assump": line.is_assump,
                "arb_consts_introduced": getattr(line, 'arb_consts_introduced', [])
            }
            proof_data["lines"].append(line_data)

        return proof_data

    def deserialize_proof(self, proof_data: dict):
        from PyQt6.QtWidgets import QLabel
        from fitch_proof_checker.view.proof_layout.proof_line_view import ProofLine
        from fitch_proof_checker.view.utils.style import ARB_CONST_LABEL_STYLE
        from fitch_proof_checker.view.proof_layout.proof_layout import update_layout

        self.fpe_main_window.goal_field.setText(proof_data.get("goal", ""))

        while self.fpe_main_window.proof_layout.count() > 0:
            item = self.fpe_main_window.proof_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        lines_data = proof_data.get("lines", [])
        for line_data in lines_data:
            is_assump = line_data.get("is_assump", False)
            depth = line_data.get("depth", 0)
            new_line = ProofLine(self.fpe_main_window, is_assump=is_assump, depth=depth)
            new_line.formula_field.setText(line_data.get("formula", ""))

            if not is_assump and hasattr(new_line, 'justification_field'):
                new_line.justification_field.setText(line_data.get("justification", ""))

            arb_consts = line_data.get("arb_consts_introduced", [])
            if arb_consts:
                new_line.arb_consts_introduced = arb_consts

                new_line.arb_const_label = QLabel()
                new_line.arb_const_label.setStyleSheet(ARB_CONST_LABEL_STYLE)
                new_line.layout().insertWidget(2, new_line.arb_const_label)
                new_line.arb_const_label.setText(" ".join(new_line.arb_consts_introduced))

            self.fpe_main_window.proof_layout.addWidget(new_line)

        update_layout(self.fpe_main_window)
