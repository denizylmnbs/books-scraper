CREAM = "#f6efe0"
CREAM_LIGHT = "#fffaf0"
TAN_BORDER = "#d9c9a3"
ESPRESSO = "#3b2a20"
ESPRESSO_LIGHT = "#4d372a"
TEXT_MUTED = "#7a6a58"
BURGUNDY = "#8c2f39"
BURGUNDY_DARK = "#732530"
GOLD = "#b8892b"
GREEN = "#3f6b4a"
RED = "#a33d3d"

MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {CREAM};
}}

QWidget {{
    font-family: "Segoe UI";
    font-size: 10.5pt;
    color: {ESPRESSO};
}}

QDialog {{
    background-color: {CREAM};
    color: {ESPRESSO};
}}

QListWidget {{
    background-color: {ESPRESSO};
    border: none;
    padding: 8px;
    outline: none;
}}

QListWidget::item {{
    padding: 9px 12px;
    border-radius: 6px;
    color: {CREAM};
}}

QListWidget::item:selected {{
    background-color: {BURGUNDY};
    color: {CREAM_LIGHT};
}}

QListWidget::item:hover:!selected {{
    background-color: {ESPRESSO_LIGHT};
}}

QLineEdit, QComboBox, QDoubleSpinBox {{
    background-color: {CREAM_LIGHT};
    border: 1px solid {TAN_BORDER};
    border-radius: 6px;
    padding: 5px 8px;
    color: {ESPRESSO};
}}

QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {BURGUNDY};
}}

QComboBox QAbstractItemView {{
    background-color: {CREAM_LIGHT};
    color: {ESPRESSO};
    selection-background-color: {BURGUNDY};
    selection-color: {CREAM_LIGHT};
}}

QScrollArea {{
    background-color: {CREAM};
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: {CREAM};
}}

QScrollBar:vertical {{
    background: {CREAM};
    width: 12px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {TAN_BORDER};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {GOLD};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QFrame#bookCard {{
    background-color: {CREAM_LIGHT};
    border: 1px solid {TAN_BORDER};
    border-radius: 10px;
}}

QFrame#bookCard:hover {{
    border: 1.5px solid {BURGUNDY};
    background-color: #fffdf5;
}}

QLabel#bookTitle {{
    font-family: "Georgia";
    font-weight: 600;
    color: {ESPRESSO};
}}

QLabel#bookCategory {{
    color: {TEXT_MUTED};
}}

QLabel#bookPrice {{
    color: {GREEN};
    font-weight: 600;
}}

QLabel#bookStars {{
    color: {GOLD};
}}

QLabel#bookStockOk {{
    color: {GREEN};
    font-size: 9pt;
}}

QLabel#bookStockOut {{
    color: {RED};
    font-size: 9pt;
}}

QLabel#dialogTitle {{
    font-family: "Georgia";
    font-size: 15pt;
    font-weight: 600;
    color: {ESPRESSO};
}}

QTextEdit {{
    background-color: {CREAM_LIGHT};
    color: {ESPRESSO};
    border: 1px solid {TAN_BORDER};
    border-radius: 6px;
    padding: 8px;
}}

QPushButton {{
    background-color: {BURGUNDY};
    color: {CREAM_LIGHT};
    border: none;
    border-radius: 6px;
    padding: 7px 18px;
}}

QPushButton:hover {{
    background-color: {BURGUNDY_DARK};
}}

QPushButton:pressed {{
    background-color: #5c1e26;
}}

QLabel#loadingLabel {{
    color: {TEXT_MUTED};
    font-style: italic;
}}
"""
