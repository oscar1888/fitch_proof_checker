from PyQt6.QtWidgets import (QFileDialog, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QPushButton,
                             QMessageBox, QComboBox)


class LogicManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        parent.lmd = self
        self.presenter = None
        self.setWindowTitle("Logic Manager")
        self.setMinimumSize(550, 400)

        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        title_label = QLabel("Active rules:")
        title_label.setStyleSheet("font-weight: bold; color: #333;")

        self.rule_list = QListWidget()

        left_layout.addWidget(title_label)
        left_layout.addWidget(self.rule_list)
        main_layout.addLayout(left_layout, stretch=2)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        default_label = QLabel("Presets:")
        default_label.setStyleSheet("font-weight: bold; color: #555;")
        right_layout.addWidget(default_label)

        self.combo_defaults = QComboBox()
        self.combo_defaults.addItems([
            "Propositional Logic (PL)",
            "First-Order Logic (FOL)"
        ])
        right_layout.addWidget(self.combo_defaults)

        self.btn_load_default = QPushButton("Load Preset")
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
        self.btn_load.clicked.connect(self._load_logic)
        right_layout.addWidget(self.btn_load)

        self.btn_save_as = QPushButton("Save logic as...")
        self.btn_save_as.clicked.connect(self._save_logic)
        right_layout.addWidget(self.btn_save_as)

        main_layout.addLayout(right_layout, stretch=1)

    def add_presenter(self, presenter):
        self.presenter = presenter
        self.presenter.populate_list()

    def _remove_rule(self):
        selected_items = self.rule_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Select the rule to remove.")
            return

        row = self.rule_list.row(selected_items[0])
        rule_name = self.presenter.get_rule_name(row)

        reply = QMessageBox.question(
            self, "Confirm deletion",
            f"Are you sure you want to remove the rule '{rule_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.presenter.remove_rule(row)

    def _load_default_logic(self):
        selected = self.combo_defaults.currentText()
        reply = QMessageBox.question(
            self, "Confirm Override",
            f"Loading '{selected}' will overwrite the current active logic. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.presenter.load_default_logic(selected)
            QMessageBox.information(self, "Success", f"Loaded preset: {selected}")

    def _add_rule(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Python Rule Plugin", "", "Python Files (*.py)")
        if not file_path: return

        success, message = self.presenter.add_rule(file_path)

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Python Plugin Error", message)

    def _load_logic(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Logic Profile", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            success, message = self.presenter.load_profile(file_path)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Error", message)

    def _save_logic(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Logic Profile As...", "",
                                                   "JSON Files (*.json);;All Files (*)")
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'

            success, message = self.presenter.save_profile(file_path)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Error", message)
