from fitch_proof_checker.view.menu_bar import view_menu, file_menu, edit_menu, proof_menu, logic_menu, help_menu


def setup_menu_bar(fpe_main_window):
    menus = [file_menu, edit_menu, view_menu, proof_menu, logic_menu, help_menu]
    for m in menus:
        m.setup(fpe_main_window)
