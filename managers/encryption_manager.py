# managers/encryption_manager.py

import base64
import logging
from cryptography.fernet import Fernet

class EncryptionManager:
    def __init__(self, file_manager, key_filename="cle_chiffrement.key"):
        """
        Gère la création/chargement de la clé de chiffrement,
        et fournit des méthodes encrypt/decrypt.
        """
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
