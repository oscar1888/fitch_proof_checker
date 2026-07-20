from PyQt6.QtWidgets import (QFileDialog, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QPushButton,
                             QMessageBox, QComboBox)


class LogicManagerDialog(QDialog):
    def __init__(self, logic_manager, parent=None):
        super().__init__(parent)
        self.logic_manager = logic_manager
        self.setWindowTitle("Logic manager")
        self.setMinimumSize(550, 400)

        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        title_label = QLabel("Active rules:")
        title_label.setStyleSheet("font-weight: bold; color: #333;")

        self.rule_list = QListWidget()
        self._populate_list()

        left_layout.addWidget(title_label)
        left_layout.addWidget(self.rule_list)
        main_layout.addLayout(left_layout, stretch=2)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        default_label = QLabel("Presets:")
        default_label.setStyleSheet("font-weight: bold; color: #555;")
        right_layout.addWidget(default_label)

        self.combo_defaults = QComboBox()
        self.combo_defaults.addItems(["Propositional Logic (PL)", "First-Order Logic (FOL)", "Minimal Logic"])
        right_layout.addWidget(self.combo_defaults)

        self.btn_load_default = QPushButton("Load Preset")
        self.btn_load_default.setStyleSheet("background-color: #fff3e0;")
        self.btn_load_default.clicked.connect(self._load_default_logic)
        right_layout.addWidget(self.btn_load_default)

        right_layout.addSpacing(15)

        rules_label = QLabel("Manage Rules:")
        rules_label.setStyleSheet("font-weight: bold; color: #555;")
        right_layout.addWidget(rules_label)

        self.btn_add = QPushButton("Add rule...")
        self.btn_add.clicked.connect(self._add_rule)
        right_layout.addWidget(self.btn_add)

        self.btn_remove = QPushButton("Remove rule")
        self.btn_remove.clicked.connect(self._remove_rule)
        right_layout.addWidget(self.btn_remove)

        right_layout.addStretch()

        self.btn_load = QPushButton("Load logic...")
        self.btn_load.setStyleSheet("background-color: #e8f5e9;")
        self.btn_load.clicked.connect(self._load_logic)
        right_layout.addWidget(self.btn_load)

        self.btn_save_as = QPushButton("Save logic as...")
        self.btn_save_as.setStyleSheet("background-color: #e8f5e9;")
        self.btn_save_as.clicked.connect(self._save_logic)
        right_layout.addWidget(self.btn_save_as)

        main_layout.addLayout(right_layout, stretch=1)

    def _populate_list(self):
        self.rule_list.clear()
        for rule in self.logic_manager.active_logic.rules:
            self.rule_list.addItem(f"{rule.name}")

    def _remove_rule(self):
        selected_items = self.rule_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Select the rule to remove.")
            return

        row = self.rule_list.row(selected_items[0])
        rule_to_remove = self.logic_manager.active_logic.rules[row]

        reply = QMessageBox.question(
            self, "Confirm deletion",
            f"Are you sure to remove the rule '{rule_to_remove.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logic_manager.active_logic.rules.pop(row)
            self._populate_list()

    def _load_default_logic(self):
        selected = self.combo_defaults.currentText()
        reply = QMessageBox.question(
            self, "Confirm Override",
            f"Loading '{selected}' will overwrite the current active logic. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Chiama il manager per caricare la logica hardcoded
            # self.logic_manager.load_preset(selected)
            self._populate_list()
            QMessageBox.information(self, "Success", f"Loaded preset: {selected}")

    def _add_rule(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Python Rule Plugin", "", "Python Files (*.py)")
        if not file_path: return

        try:
            module_name = os.path.basename(file_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            custom_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(custom_module)

            if not hasattr(custom_module, 'CustomRule'):
                raise ValueError("The Python file must contain a class named 'CustomRule'.")

            new_rule = custom_module.CustomRule()

            if not hasattr(new_rule, 'check') or not callable(getattr(new_rule, 'check')):
                raise ValueError(
                    "The 'CustomRule' class must implement a 'check(derived_lines, conclusion_line)' method.")

            self.logic_manager.active_logic.rules.append(new_rule)
            self._populate_list()

            QMessageBox.information(self, "Success", f"Rule '{new_rule.name}' loaded successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Python Plugin Error", f"Failed to load custom rule:\n\n{str(e)}")

    def _load_logic(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Logic Profile", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            QMessageBox.information(self, "Mock", "Profile loaded.")

    def _save_logic(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Logic Profile As...", "",
                                                   "JSON Files (*.json);;All Files (*)")
        if file_name:
            QMessageBox.information(self, "Mock", "Profile saved.")
