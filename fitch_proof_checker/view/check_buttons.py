from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QPushButton


def setup_check_buttons(fpe_main_window):
    top_bar_layout = QHBoxLayout()
    top_bar_layout.addStretch()
    fpe_main_window.btn_check_step = QPushButton("Check Step")
    fpe_main_window.btn_check_step.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    fpe_main_window.btn_check_proof = QPushButton("Check Proof")
    fpe_main_window.btn_check_proof.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    fpe_main_window.btn_check_step.setMinimumHeight(40)
    fpe_main_window.btn_check_proof.setMinimumHeight(40)
    fpe_main_window.btn_check_step.setMinimumWidth(180)
    fpe_main_window.btn_check_proof.setMinimumWidth(180)
    top_bar_layout.addWidget(fpe_main_window.btn_check_step)
    top_bar_layout.addSpacing(15)
    top_bar_layout.addWidget(fpe_main_window.btn_check_proof)
    top_bar_layout.addStretch()
    fpe_main_window.global_layout.addLayout(top_bar_layout)
