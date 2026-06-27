import os
import importlib.util

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QMessageBox, QTabWidget, QWidget,
                             QFileDialog, QComboBox, QLabel, QSizePolicy)


class GrammarManagerDialog(QDialog):
    def __init__(self, grammar_manager, parent=None):
        super().__init__(parent)
        self.grammar_manager = grammar_manager
        self.setWindowTitle("Grammar Manager")
        self.setMinimumSize(500, 450)

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        self.tab_connectives = QWidget()
        self.tab_quantifiers = QWidget()

        self.tabs.addTab(self.tab_connectives, "Connectives")
        self.tabs.addTab(self.tab_quantifiers, "Quantifiers")

        self._setup_connectives_tab()
        self._setup_quantifiers_tab()

        main_layout.addWidget(self.tabs)

        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(10)

        preset_layout = QHBoxLayout()
        preset_label = QLabel("Default Grammars:")
        preset_label.setStyleSheet("font-weight: bold; color: #555;")

        self.combo_defaults = QComboBox()
        self.combo_defaults.addItems([
            "Propositional Logic (PL)",
            "First-Order Logic (FOL)",
            "Modal Logic"
        ])
        self.combo_defaults.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.btn_load_default = QPushButton("Load Preset")
        self.btn_load_default.clicked.connect(self._load_default_grammar)

        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.combo_defaults)
        preset_layout.addWidget(self.btn_load_default)

        profile_layout = QHBoxLayout()
        self.btn_load_profile = QPushButton("Load Grammar Profile...")
        self.btn_load_profile.setStyleSheet("background-color: #e8f5e9;")

        self.btn_save_profile = QPushButton("Save Grammar Profile As...")
        self.btn_save_profile.setStyleSheet("background-color: #e8f5e9;")

        self.btn_load_profile.clicked.connect(self._load_profile)
        self.btn_save_profile.clicked.connect(self._save_profile)

        profile_layout.addStretch()
        profile_layout.addWidget(self.btn_load_profile)
        profile_layout.addWidget(self.btn_save_profile)

        bottom_layout.addLayout(preset_layout)
        bottom_layout.addLayout(profile_layout)

        main_layout.addLayout(bottom_layout)

    def _setup_connectives_tab(self):
        layout = QHBoxLayout(self.tab_connectives)

        self.list_connectives = QListWidget()
        self._populate_list('connectives')

        btn_layout = QVBoxLayout()
        btn_add = QPushButton("Add Connective...")
        btn_remove = QPushButton("Remove Connective")

        btn_add.clicked.connect(lambda: self._add_item('connective'))
        btn_remove.clicked.connect(lambda: self._remove_item('connective'))

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addStretch()

        layout.addWidget(self.list_connectives, stretch=2)
        layout.addLayout(btn_layout, stretch=1)

    def _setup_quantifiers_tab(self):
        layout = QHBoxLayout(self.tab_quantifiers)

        self.list_quantifiers = QListWidget()
        self._populate_list('quantifiers')

        btn_layout = QVBoxLayout()
        btn_add = QPushButton("Add Quantifier...")
        btn_remove = QPushButton("Remove Quantifier")

        btn_add.clicked.connect(lambda: self._add_item('quantifier'))
        btn_remove.clicked.connect(lambda: self._remove_item('quantifier'))

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addStretch()

        layout.addWidget(self.list_quantifiers, stretch=2)
        layout.addLayout(btn_layout, stretch=1)

    def _populate_list(self, item_type):
        if item_type == 'connectives':
            self.list_connectives.clear()
            for conn in getattr(self.grammar_manager, 'connectives', []):
                self.list_connectives.addItem(f"{conn.name} ({conn.symbol})")
        else:
            self.list_quantifiers.clear()
            for quant in getattr(self.grammar_manager, 'quantifiers', []):
                self.list_quantifiers.addItem(f"{quant.name} ({quant.symbol})")

    def _remove_item(self, item_type):
        list_widget = self.list_connectives if item_type == 'connective' else self.list_quantifiers
        target_list = self.grammar_manager.connectives if item_type == 'connective' else self.grammar_manager.quantifiers

        selected_items = list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", f"Select a {item_type} to remove.")
            return

        row = list_widget.row(selected_items[0])
        item_to_remove = target_list[row]

        reply = QMessageBox.question(
            self, "Confirm deletion",
            f"Are you sure you want to remove '{item_to_remove.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            target_list.pop(row)
            self._populate_list(item_type + 's')

    def _add_item(self, item_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select Python {item_type.capitalize()} Plugin",
            "",
            "Python Files (*.py)"
        )

        if not file_path:
            return

        try:
            module_name = os.path.basename(file_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            custom_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(custom_module)

            expected_class = 'CustomConnective' if item_type == 'connective' else 'CustomQuantifier'

            if not hasattr(custom_module, expected_class):
                raise ValueError(f"The file must contain a class named '{expected_class}'.")

            new_item = getattr(custom_module, expected_class)()

            if item_type == 'connective':
                self.grammar_manager.connectives.append(new_item)
                self._populate_list('connectives')
            else:
                self.grammar_manager.quantifiers.append(new_item)
                self._populate_list('quantifiers')

            QMessageBox.information(self, "Success", f"{item_type.capitalize()} '{new_item.name}' loaded!")

        except Exception as e:
            QMessageBox.critical(self, "Plugin Error", f"Failed to load {item_type}:\n\n{str(e)}")

    def _load_default_grammar(self):
        selected = self.combo_defaults.currentText()
        reply = QMessageBox.question(
            self, "Confirm Override",
            f"Loading '{selected}' will overwrite the current grammar configuration. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Chiama il manager per caricare l'alfabeto hardcoded
            # self.grammar_manager.load_preset(selected)

            self._populate_list('connectives')
            self._populate_list('quantifiers')

            QMessageBox.information(self, "Success", f"Loaded preset: {selected}")

    def _load_profile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Grammar Profile", "",
                                                   "JSON Files (*.json);;All Files (*)")
        if file_name:
            # TODO: self.grammar_manager.load_vocabulary_from_json(file_name)
            QMessageBox.information(self, "Mock", "Grammar Profile loaded.")
            self._populate_list('connectives')
            self._populate_list('quantifiers')

    def _save_profile(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Grammar Profile As...", "",
                                                   "JSON Files (*.json);;All Files (*)")
        if file_name:
            # TODO: self.grammar_manager.save_vocabulary_to_json(file_name)
            QMessageBox.information(self, "Mock", "Grammar Profile saved.")
