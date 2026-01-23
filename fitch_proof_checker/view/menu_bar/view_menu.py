from fitch_proof_checker.view.utils import add_action


def setup(fpe_main_window):
    view_menu = fpe_main_window.menuBar().addMenu("&View")
    action_data = [
        ("Zoom In", zoom_in, "Ctrl++"),
        ("Zoom Out", zoom_out, "Ctrl+-"),
    ]
    for name, fun, shortcut in action_data:
        add_action(fpe_main_window, view_menu, '&' + name, fun, shortcut)


def zoom_in(fpe_main_window):
    fpe_main_window.zoom_level += 1
    apply_zoom(fpe_main_window)


def zoom_out(fpe_main_window):
    fpe_main_window.zoom_level -= 1
    apply_zoom(fpe_main_window)


def apply_zoom(fpe_main_window):
    base_size = 10
    new_size = max(6, base_size + fpe_main_window.zoom_level)
    font = fpe_main_window.central_widget.font()
    font.setPointSize(new_size)
    fpe_main_window.central_widget.setFont(font)
