# ui/themes.py

THEMES = {
    "Modern Dark": """
    QMainWindow {
        background-color: #2b2f38;
    }
    QFrame#TopBar {
        background-color: #2f353f;
        min-height: 40px;
    }
    QLabel#TopBarTitle {
        color: #f0f0f0;
        font-size: 16px;
        font-weight: bold;
    }
    QToolButton {
        background: transparent;
        color: #f0f0f0;
    }
    QToolButton:hover {
        background-color: #3a3f48;
    }
    QFrame#SideBar {
        background-color: #21252b;
    }
    QPushButton#SideBarButton {
        background-color: transparent;
        border: none;
        text-align: left;
        padding: 8px 20px;
        font-size: 14px;
        color: #c8c8c8;
    }
    QPushButton#SideBarButton:hover {
        background-color: #2d333b;
    }
    QPushButton#SideBarButton:checked {
        background-color: #38414a;
    }
    QFrame#ContentArea {
        background-color: #2b2f38;
    }
    QFrame#Card {
        background-color: #2f3542;
        border-radius: 5px;
    }
    QLabel {
        color: #dddddd;
    }
    QTextEdit {
        background-color: #3b3f48;
        border: 1px solid #565a63;
        border-radius: 4px;
        color: #ffffff;
    }
    QLineEdit {
        background-color: #3b3f48;
        border: 1px solid #565a63;
        border-radius: 4px;
        color: #ffffff;
        padding: 4px;
    }
    QLabel#StatusLabel {
        font-size:16px;
        font-weight:bold;
    }
    QDialog, QMessageBox {
        background-color: #FFFFFF;
        color: #000000;
    }
    QDialog QLabel, QMessageBox QLabel {
        color: #000000;
    }
    """,

    "Light": """
    QMainWindow {
        background-color: #f0f0f0;
    }
    QFrame#TopBar {
        background-color: #dadada;
        min-height: 40px;
    }
    QLabel#TopBarTitle {
        color: #333333;
        font-size: 16px;
        font-weight: bold;
    }
    QToolButton {
        background: transparent;
        color: #333333;
    }
    QToolButton:hover {
        background-color: #e0e0e0;
    }
    QFrame#SideBar {
        background-color: #eeeeee;
    }
    QPushButton#SideBarButton {
        background-color: transparent;
        border: none;
        text-align: left;
        padding: 8px 20px;
        font-size: 14px;
        color: #444444;
    }
    QPushButton#SideBarButton:hover {
        background-color: #dddddd;
    }
    QPushButton#SideBarButton:checked {
        background-color: #cccccc;
    }
    QFrame#ContentArea {
        background-color: #f0f0f0;
    }
    QFrame#Card {
        background-color: #ffffff;
        border-radius: 5px;
        border: 1px solid #cccccc;
    }
    QLabel {
        color: #333333;
    }
    QTextEdit {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        color: #000000;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        color: #000000;
        padding: 4px;
    }
    QLabel#StatusLabel {
        font-size:16px;
        font-weight:bold;
        color: #333333;
    }
    QDialog, QMessageBox {
        background-color: #FFFFFF;
        color: #000000;
    }
    QDialog QLabel, QMessageBox QLabel {
        color: #000000;
    }
    """,

    "Blue": """
    QMainWindow {
        background-color: #dcefff;
    }
    QFrame#TopBar {
        background-color: #4a90e2;
        min-height: 40px;
    }
    QLabel#TopBarTitle {
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
    }
    QToolButton {
        background: transparent;
        color: #ffffff;
    }
    QToolButton:hover {
        background-color: #5ba1f2;
    }
    QFrame#SideBar {
        background-color: #375a7f;
    }
    QPushButton#SideBarButton {
        background-color: transparent;
        border: none;
        text-align: left;
        padding: 8px 20px;
        font-size: 14px;
        color: #dcefff;
    }
    QPushButton#SideBarButton:hover {
        background-color: #2c4866;
    }
    QPushButton#SideBarButton:checked {
        background-color: #203650;
    }
    QFrame#ContentArea {
        background-color: #dcefff;
    }
    QFrame#Card {
        background-color: #ffffff;
        border-radius: 5px;
        border: 1px solid #aaccee;
    }
    QLabel {
        color: #333333;
    }
    QTextEdit {
        background-color: #ffffff;
        border: 1px solid #aaccee;
        border-radius: 4px;
        color: #000000;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #aaccee;
        border-radius: 4px;
        color: #000000;
        padding: 4px;
    }
    QLabel#StatusLabel {
        font-size:16px;
        font-weight:bold;
        color: #375a7f;
    }
    QDialog, QMessageBox {
        background-color: #FFFFFF;
        color: #000000;
    }
    QDialog QLabel, QMessageBox QLabel {
        color: #000000;
    }
    """,

    "Green": """
    QMainWindow {
        background-color: #e9f8ec;
    }
    QFrame#TopBar {
        background-color: #2ecc71;
        min-height: 40px;
    }
    QLabel#TopBarTitle {
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
    }
    QToolButton {
        background: transparent;
        color: #ffffff;
    }
    QToolButton:hover {
        background-color: #34d585;
    }
    QFrame#SideBar {
        background-color: #27ae60;
    }
    QPushButton#SideBarButton {
        background-color: transparent;
        border: none;
        text-align: left;
        padding: 8px 20px;
        font-size: 14px;
        color: #e9f8ec;
    }
    QPushButton#SideBarButton:hover {
        background-color: #229a54;
    }
    QPushButton#SideBarButton:checked {
        background-color: #1f8a4b;
    }
    QFrame#ContentArea {
        background-color: #e9f8ec;
    }
    QFrame#Card {
        background-color: #ffffff;
        border-radius: 5px;
        border: 1px solid #a2e2b4;
    }
    QLabel {
        color: #2c3e50;
    }
    QTextEdit {
        background-color: #ffffff;
        border: 1px solid #a2e2b4;
        border-radius: 4px;
        color: #2c3e50;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #a2e2b4;
        border-radius: 4px;
        color: #2c3e50;
        padding: 4px;
    }
    QLabel#StatusLabel {
        font-size:16px;
        font-weight:bold;
        color: #27ae60;
    }
    QDialog, QMessageBox {
        background-color: #FFFFFF;
        color: #000000;
    }
    QDialog QLabel, QMessageBox QLabel {
        color: #000000;
    }
    """
}
