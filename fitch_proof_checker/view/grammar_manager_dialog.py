from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QMessageBox, QTabWidget, \
                            QWidget, QFileDialog, QComboBox, QLabel, QSizePolicy


class GrammarManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        parent.gmd = self
        self.presenter = None
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
        ])
        self.combo_defaults.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.btn_load_default = QPushButton("Load Preset")
        self.btn_load_default.clicked.connect(self._load_default_grammar)

        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.combo_defaults)
        preset_layout.addWidget(self.btn_load_default)

        profile_layout = QHBoxLayout()
        self.btn_load_profile = QPushButton("Load Grammar Profile...")

        self.btn_save_profile = QPushButton("Save Grammar Profile As...")

        self.btn_load_profile.clicked.connect(self._load_profile)
        self.btn_save_profile.clicked.connect(self._save_profile)

        profile_layout.addStretch()
        profile_layout.addWidget(self.btn_load_profile)
        profile_layout.addWidget(self.btn_save_profile)

        bottom_layout.addLayout(preset_layout)
        bottom_layout.addLayout(profile_layout)

        main_layout.addLayout(bottom_layout)

    def add_presenter(self, presenter):
        self.presenter = presenter
        self.presenter.populate_list('connective')
        self.presenter.populate_list('quantifier')

    def _setup_connectives_tab(self):
        layout = QHBoxLayout(self.tab_connectives)

        self.list_connectives = QListWidget()

        btn_layout = QVBoxLayout()
        btn_add = QPushButton("Add Connective...")
        btn_remove = QPushButton("Remove Connective")

        self.btn_add_conn = btn_add
        self.btn_remove_conn = btn_remove

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

        btn_layout = QVBoxLayout()
        btn_add = QPushButton("Add Quantifier...")
        btn_remove = QPushButton("Remove Quantifier")

        self.btn_add_quant = btn_add
        self.btn_remove_quant = btn_remove

        btn_add.clicked.connect(lambda: self._add_item('quantifier'))
        btn_remove.clicked.connect(lambda: self._remove_item('quantifier'))

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addStretch()

        layout.addWidget(self.list_quantifiers, stretch=2)
        layout.addLayout(btn_layout, stretch=1)

    def _remove_item(self, item_type):
        list_widget = self.list_connectives if item_type == 'connective' else self.list_quantifiers
        selected_items = list_widget.selectedItems()

        if not selected_items:
            clean_type = item_type.replace('_', ' ')
            QMessageBox.warning(self, "Warning", f"Select a {clean_type} to remove.")
            return

        row = list_widget.row(selected_items[0])
        item_name = self.presenter.get_item_name(item_type, row)

        if self.presenter.is_protected_item(item_type, row):
            QMessageBox.warning(
                self,
                "Action Denied",
                f"Cannot remove '{item_name}' because it is a core First-Order Logic component."
            )
            return

        reply = QMessageBox.question(
            self, "Confirm deletion",
            f"Are you sure you want to remove '{item_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.presenter.remove_item(item_type, row)

    def _add_item(self, item_type):
        clean_type = item_type.capitalize()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select Python {clean_type} Plugin",
            "",
            "Python Files (*.py)"
        )

        if not file_path:
            return

        success, message = self.presenter.add_item(item_type, file_path)

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Plugin Error", message)

    def _load_default_grammar(self):
        selected = self.combo_defaults.currentText()
        reply = QMessageBox.question(
            self, "Confirm Override",
            f"Loading '{selected}' will overwrite the current grammar configuration. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.presenter.load_default_grammar(selected)
            QMessageBox.information(self, "Success", f"Loaded preset: {selected}")

    def _load_profile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Grammar Profile", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            success, message = self.presenter.load_profile(file_path)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Error", message)

    def _save_profile(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Grammar Profile As...", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'

            success, message = self.presenter.save_profile(file_path)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Error", message)
