import json
import os

from PyQt6.QtWidgets import (QFileDialog, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QPushButton,
                             QMessageBox)


class LogicManagerDialog(QDialog):
    def __init__(self, logic_manager, parent=None):
        super().__init__(parent)
        self.logic_manager = logic_manager
        self.setWindowTitle(f"Logic manager")
        self.setMinimumSize(500, 350)

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

        self.btn_add = QPushButton("Add rule...")
        self.btn_remove = QPushButton("Remove rule")

        self.btn_add.setStyleSheet("background-color: #e1f5fe; font-weight: bold;")

        right_layout.addWidget(self.btn_add)
        right_layout.addWidget(self.btn_remove)

        right_layout.addStretch()

        self.btn_load = QPushButton("Load logic...")
        self.btn_load.setStyleSheet("background-color: #e8f5e9;")
        right_layout.addWidget(self.btn_load)
        self.btn_save_as = QPushButton("Save logic as...")
        self.btn_save_as.setStyleSheet("background-color: #e8f5e9;")
        right_layout.addWidget(self.btn_save_as)

        main_layout.addLayout(right_layout, stretch=1)

        self.btn_remove.clicked.connect(self._remove_rule)
        self.btn_add.clicked.connect(self._add_rule)
        self.btn_save_as.clicked.connect(self._save_logic)
        self.btn_load.clicked.connect(self._load_logic)

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

    def _add_rule(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select JSON Rule File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # TODO: implement this
            """
            # Aggiungiamo al backend e aggiorniamo la UI
            self.logic_manager.active_logic.rules.append(new_rule)
            self._populate_list()

            QMessageBox.information(
                self,
                "Success",
                f"Rule '{new_rule.name}' loaded successfully!"
            )
            """

        except Exception as e:
            QMessageBox.critical(
                self,
                "JSON Import Error",
                f"Failed to load rule from {os.path.basename(file_path)}:\n\n{str(e)}"
            )

    def _load_logic(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Logic Profile", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            try:
                # TODO: Chiama il manager per caricare dal JSON
                # self.logic_manager.load_logic_from_json(file_name)
                self._populate_list()
                QMessageBox.information(self, "Success", "Logic profile loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load logic:\n{str(e)}")

    def _save_logic(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Logic Profile As...", "",
                                                   "JSON Files (*.json);;All Files (*)")
        if file_name:
            try:
                # TODO: Chiama il manager per salvare l'active_logic su file
                # self.logic_manager.save_logic_to_json(file_name)
                QMessageBox.information(self, "Success", "Logic profile saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save logic:\n{str(e)}")
