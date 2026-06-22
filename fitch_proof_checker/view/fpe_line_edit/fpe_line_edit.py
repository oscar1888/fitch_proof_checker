from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QLineEdit

from fitch_proof_checker.view.utils.style import qle_font


class FPELineEdit(QLineEdit):
    def __init__(self, proof_line, fpe_main_window):
        super().__init__()
        self.fpe_main_window = fpe_main_window
        self.proof_line = proof_line
        self.setFont(qle_font)
        self.textEdited.connect(self._on_text_edited)

    def _on_text_edited(self, text):
        self.fpe_main_window.edited = True
        self._auto_replace_symbols(text)

    def _auto_replace_symbols(self, text):
        from fitch_proof_checker.view.fpe_line_edit.utils import symbol_map

        new_text = text
        for ascii_seq, (_, symbol) in symbol_map.items():
            if ascii_seq in new_text:
                new_text = new_text.replace(ascii_seq, symbol)

        if new_text != text:
            cursor_pos = self.cursorPosition()
            diff = len(new_text) - len(text)

            self.setText(new_text)
            self.setCursorPosition(cursor_pos + diff)

    def contextMenuEvent(self, event):
        from fitch_proof_checker.view.fpe_line_edit.utils import symbol_map
        menu = self.createStandardContextMenu()
        menu.addSeparator()

        logic_menu = menu.addMenu("Insert Logic Symbol")
        symbols_to_add = [(f'{d} ({s})', s) for d, s in symbol_map.values()]

        for name, char in symbols_to_add:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, c=char: self.insert(c))
            logic_menu.addAction(action)

        menu.exec(event.globalPos())

    def keyPressEvent(self, event):
        from fitch_proof_checker.view.fpe_line_edit.utils import shortcuts_conds

        for cond, act in shortcuts_conds:
            if cond(event):
                act(self.fpe_main_window)
                return

        super().keyPressEvent(event)
