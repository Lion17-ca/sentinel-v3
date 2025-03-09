# ui/dialogs.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QLabel, QComboBox,
    QSpinBox, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt

class SettingsDialog(QDialog):
    """
    Boîte de dialogue "Paramètres" pour configurer quelques options.
    + Sélecteur de thème (4 thèmes)
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
            "<h3>Sentinel v3.0</h3>"
            "<p>Application de monitoring et keylogger.</p>"
            "<p><b>Auteur :</b> Emmanuel Angrevier</p>"
            #"<p><b>Site :</b> <a href='https://example.com'>example.com</a></p>"
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
