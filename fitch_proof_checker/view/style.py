BASE_SIZE = 10
MIN_SIZE = 8
MAX_SIZE = 12

BASE_QLE_SIZE = 12


def apply(fpe_main_window):
    fpe_main_window.setStyleSheet("""    
    QLineEdit {
        border: none;
        border-bottom: 1px solid #ccc;
        background: transparent;
        padding: 6px 0;
    }
    
    QLineEdit:focus {
        border-bottom: 2px solid #0078d7;
        background-color: #f0f8ff;
    }
    """)
