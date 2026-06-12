from PyQt6.QtWidgets import QApplication
from fitch_proof_checker.view.utils.style import MIN_SIZE, BASE_SIZE, MAX_SIZE, BASE_QLE_SIZE
from fitch_proof_checker.view.utils import add_action


def setup(fpe_main_window):
    view_menu = fpe_main_window.menuBar().addMenu("View")
    action_data = [
        ("Zoom In", apply_zoom(+1), "Ctrl++"),
        ("Zoom Out", apply_zoom(-1), "Ctrl+-"),
    ]
    for name, fun, shortcut in action_data:
        add_action(fpe_main_window, view_menu, name, fun, shortcut)


def apply_zoom(zoom):
    def _apply_zoom(fpe_main_window):
        if not (MIN_SIZE <= BASE_SIZE + fpe_main_window.zoom_level + zoom <= MAX_SIZE):
            return
        fpe_main_window.zoom_level += zoom
        QApplication.instance().setStyleSheet(
            f"""
            * {{ font-size: {BASE_SIZE + fpe_main_window.zoom_level}pt; }}
            QLineEdit {{font-size: {BASE_QLE_SIZE + fpe_main_window.zoom_level}pt; }}
            """
        )
    return _apply_zoom
